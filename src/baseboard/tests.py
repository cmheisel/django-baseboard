import random, pprint, os

import feedparser

from django.test import TestCase
from django.template.defaultfilters import force_escape

from baseboard.models import Project, Dashboard, RSSFeed
from baseboard.mocks import TestBasecampProject

class BaseboardTestHelper(TestCase):
    urls = 'baseboard.urls'

    def setUp(self):
        random.seed()
        self.object_indexes = []
        self._mock_basecamp_access()
        self.project = self.create_project()
        super(BaseboardTestHelper, self).setUp()

    def tearDown(self):
        self._unmock_basecamp_access()
        super(BaseboardTestHelper, self).tearDown()

    def object_index(self, max=1000):
        result = random.randint(0, max)

        if len(self.object_indexes) >= max:
            raise Exception("""You've run out of unqiue object indexes. 
                    Try raising max: %s""" % max)
        
        if result not in self.object_indexes:
            #We've got a live one here
            self.object_indexes.append(result)
            return result
        else:
            return self.object_index() #Recurse until you find an unused integer

    def _mock_basecamp_access(self, klass=TestBasecampProject):
        """Monkey patches Project.Basecamp for testing."""
        self._real_Basecamp = Project.BasecampProject
        Project.BasecampProject = klass

    def _unmock_basecamp_access(self):
        """Undoes the Project.Basecamp monkeypatching."""
        Project.BasecampProject = self._real_Basecamp    

    def create_project(self, **kwargs):
        """Creates a Project instance, using valid test 
        defaults unless overridden in **kwargs."""
        save = kwargs.get('save', True) 
        if kwargs.has_key('save'):
            del(kwargs['save'])

        index = self.object_index()
        defaults = dict(slug = "test-project-%s" % index,
            basecamp_url = "https://foo.basecamphq.com/projects/%s/log" % index)
        defaults.update(kwargs)
        p = Project(**defaults)

        if save:
            p.save()
            self.assert_(p.id)
        return p

    def create_dashboard(self, save=True, **kwargs):
        """Create a Dashboard object, using the optional kwargs. If save=False the object is returned without saving."""
        index = self.object_index()
        if not kwargs: kwargs = dict(name="Test Dashboard %s" % index, slug="test-dashboard-%s" % index)
        d = Dashboard(**kwargs)

        if not save: return d
        
        d.save()
        self.assert_(d.id) #Cheap validity check
        return d


class ProjectUnitTests(BaseboardTestHelper):
    url_parsing_tests = {
        "valid": ('https://foo.updatelog.com/projects/2907852/posts/20924136/comments',
                  'https://foo.updatelog.com/projects/2907852/project/log/',
                  'https://foo.updatelog.com/projects/2907852/posts',
                  'https://foo.updatelog.com/projects/2907852/posts/20924136/comments',
                  'https://foo.updatelog.com/projects/2907852/chat/pick_room'),
        "invalid": ('https://foo.updatelog.com/clients', 'http://anotherdomain.updatelog.com'),
    }
            
    def test_create_project(self):
        p = self.create_project()
        self.assertNotEqual(None, p.id)

        p = self.create_project(save=False)
        self.assertEqual(None, p.id)
        p.save()
        self.assert_(p.id)

    def test_project_url(self):
        p = self.create_project(basecamp_url="https://foo.updatelog.com/projects/2984915/companies")
        
        expected = "https://foo.updatelog.com/projects/2984915/project/log"
        self.assertEqual(expected, p.project_url)

    def test_project_id_detection(self):
        """When given a proper URL it should be able to set it's project_id field."""
        tests = {
            2907852: self.url_parsing_tests['valid'],
            None: self.url_parsing_tests['invalid'],
        }
        
        for basecamp_id, test_cases in tests.items():
            for case in test_cases:
                actual = Project.extract_basecamp_id(case)
                msg = "%s != %s Test case: %s" % (basecamp_id, actual, case)
                self.assertEqual(basecamp_id, actual, msg)

    def test_basecamp_api_url(self):
        tests = {
            'https://foo.updatelog.com/': self.url_parsing_tests['valid'],
            'http://foo.updatelog.com/': ['http://foo.updatelog.com/projects/8130456/', ],
        }
        for domain, test_cases in tests.items():
            for case in test_cases:
                actual = Project.extract_basecamp_api_url(case)
                msg = "%s != %s for test case %s" % (domain, actual, case)
                self.assertEqual(domain, actual, msg)

    def test_name_detection(self):
        """If no name is provided, it should be loaded from Basecamp."""
        self.project.name = ''
        self.project.detect_name()
        self.assertEqual("Kobol's Last Gleaming", self.project.name)

    def test_auto_slug(self):
        p = self.create_project(save=False,
                                name="Kobol's Last Gleaming",
                                basecamp_url='https://foo.basecamphq.com/projects/1701/log/',
                                basecamp_id=None,                                
                                slug='')
        p.save()
        self.assertNotEqual('', p.slug)

    def test_save(self):
        """Name and basecamp_id should be populated if URL provided."""
        p = self.create_project(save=False,
                                basecamp_url='https://foo.basecamphq.com/projects/1701/log/',
                                basecamp_id=None,
                                name='')
        p.save()
        self.assertEqual(1701, p.basecamp_id)
        self.assertEqual("Kobol's Last Gleaming", p.name)


class ProjectSummaryTests(BaseboardTestHelper):
    def test_summary_updates(self):
        """When fetched a summary should be present and the record
        should show that it is updated."""
        
        self.project.update_summary()

        self.project = Project.objects.get(id=self.project.id) #Reload from db

        self.assertNotEqual(None, self.project.basecamp_updated_at)
        self.assert_(self.project.summary, "There should be a populated project summary.")
        self.assert_(len(self.project.summary.keys()) > 0, "There should be at least 1 key in the summary dict.")

        expected = pprint.pformat(self.project.summary)
        self.assertEqual(expected, self.project.readable_summary)
        

class DashboardUnitTests(BaseboardTestHelper):
    def test_str(self):
        d = self.create_dashboard(name="Test Dashboard", slug="test-dashboard")
        expected = "Test Dashboard"
        actual = str(d)

        self.assertEqual(actual, expected)

class BaseboardFunctionalTests(BaseboardTestHelper):
    def test_index(self):
        d = self.create_dashboard()
        
        r = self.client.get('/')
        self.assertContains(r, d.name)
        self.assertContains(r, d.get_absolute_url())

    def test_dashboard_detail(self):
        test_url = '/dashboard/%s/'
        
        d = self.create_dashboard()
        d.description = "This is a test dashboard."
        d.save()

        r = self.client.get(test_url % d.slug)
        self.assertContains(r, d.name)
        self.assertContains(r, d.description)
        
        p1 = self.create_project()
        p1.save()
        p2 = self.create_project()
        p2.save()
        d.projects = [ p1, p2 ]
        d.save()

        r = self.client.get(test_url % d.slug)
        self.assertContains(r, "There aren't any projects associated with this dashboard.", 0)
        self.assertContains(r, force_escape(p1.name))
        self.assertContains(r, force_escape(p2.name))
        self.assertContains(r, d.projects.all()[0].get_absolute_url())

    def test_project_detail(self):
        test_url = "/project/%s/"

        r = self.client.get(test_url % self.project.slug)
        self.assertContains(r, force_escape(self.project.name))
        self.assertContains(r, self.project.description)

class RSSFeedTests(BaseboardTestHelper):
    _rss_fixtures = ('default.xml', )
    _feeds = None

    def setUp(self):
        self.fixtures_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        if not self._feeds:
            self._feeds = self._setup_test_feeds()
        super(RSSFeedTests, self).setUp()

    def _setup_test_feeds(self):
        feeds = {}

        for filename in self._rss_fixtures:
            feeds[filename] = feedparser.parse(self._feed_fixture(filename))
        return feeds

    def create_feed(self, **kwargs):
        save = kwargs.get('save', True)
        if kwargs.has_key('save'):
            del(kwargs['save'])

        if kwargs.has_key('url'):
            kwargs['url'] = self._feed_fixture(kwargs['url'])
        
        defaults = {
            'url': self._feed_fixture('default.xml')
        }
        defaults.update(kwargs)
        feed = RSSFeed(**defaults)

        if save:
            feed.save()
            self.assert_(feed.id)
        return feed

    def _feed_fixture(self, filename):
        return os.path.join(self.fixtures_path, filename)
        
    def test_parsing(self):
        feed = self.create_feed()
        feed.update_feed()
        self.assert_(feed.parsed_at)
        self.assert_(feed.contents)
        self.assertEqual(None, feed.info.get('bozo_exception', None))
        
    def test_name_detection(self):
        feed = self.create_feed(name=None)
        self.assertEqual(feed.name, self._feeds['default.xml']['feed']['title'])
    
def runtests():
    import os
    cmd = "%s/../../bin/test" % (os.path.abspath(os.path.dirname(__file__)))
    os.system(cmd)

if __name__ == "__main__":
    runtests()
