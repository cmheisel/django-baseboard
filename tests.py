import random

from django.test import TestCase

from basecampreporting.mocks import TestProject
from baseboard.models import Project, Dashboard

class BaseboardTestHelper(TestCase):
    def setUp(self):
        random.seed()
        self.object_indexes = []
        super(BaseboardTestHelper, self).setUp()

    def tearDown(self):
        super(BaseboardTestHelper, self).tearDown()

    def object_index(self, max=1000):
        result = random.randint(0, max)

        if len(self.object_indexes) >= max:
            raise Exception("You've run out of unqiue object indexes. Try raising max: %s" % max)
        
        if result not in self.object_indexes:
            #We've got a live one here
            self.object_indexes.append(result)
            return result
        else:
            return self.object_index() #Recurse until you find an unused integer

class ProjectUnitTests(BaseboardTestHelper):
    url_parsing_tests = {
        "valid": ('https://foo.updatelog.com/projects/2907852/posts/20924136/comments',
                  'https://foo.updatelog.com/projects/2907852/project/log/',
                  'https://foo.updatelog.com/projects/2907852/posts',
                  'https://foo.updatelog.com/projects/2907852/posts/20924136/comments',
                  'https://foo.updatelog.com/projects/2907852/chat/pick_room'),
        "invalid": ('https://foo.updatelog.com/clients', ),
    }

    def setUp(self):
        super(ProjectUnitTests, self).setUp()
        self._mock_basecamp_access()
        self.project = self.create_project()

    def tearDown(self):
        self._unmock_basecamp_access()

    def _mock_basecamp_access(self):
        """Monkey patches Project.Basecamp for testing."""
        self._real_Basecamp = Project.Basecamp
        Project.Basecamp = TestProject

    def _unmock_basecamp_access(self):
        """Undoes the Project.Basecamp monkeypatching."""
        Project.Basecamp = self._real_Basecamp
    
    def create_project(self, save=True, **kwargs):
        """Creates a Project instance, using valid test defaults unless overridden in **kwargs."""
        index = self.object_index()
        if not kwargs:
            kwargs = dict(name = "Test Project %s" % index,
                          slug = "test-project-%s" % index,
                          basecamp_url = "https://foo.basecamphq.com/projects/%s/log" % index,
                          basecamp_id = index)
        p = Project(**kwargs)

        if not save: return p

        p.save()
        self.assert_(p.id)
        return p
            
    def test_create_project(self):
        p = self.create_project()
        self.assertNotEqual(None, p.id)

        p = self.create_project(save=False)
        self.assertEqual(None, p.id)
        p.save()
        self.assert_(p.id)

    def test_project_id_detection(self):
        """When given a proper URL it should be able to set it's project_id field."""
        tests = {
            2907852: self.url_parsing_tests['valid'],
            None: self.url_parsing_tests['invalid'],
        }
        
        for basecamp_id, test_cases in tests.items():
            for case in test_cases:
                p = self.create_project(save=False, basecamp_id=None)
                p.basecamp_url = case
                p.detect_basecamp_id()
                msg = "%s != %s Test case: %s" % (p.basecamp_id, basecamp_id, case)
                self.assertEqual(p.basecamp_id, basecamp_id, msg)

    def test_api_url_(self):
        tests = {
            'https://foo.updatelog.com/': self.url_parsing_tests['valid'],
            'http://foo.updatelog.com/': ['http://foo.updatelog.com/projects/8130456/', ],
            None: self.url_parsing_tests['invalid'],
        }
        for domain, test_cases in tests.items():
            for case in test_cases:
                p = self.create_project(save=False, basecamp_id=None)
                p.basecamp_url = case
                self.assertEqual(domain, p.basecamp_api_url)

    def ztest_name_detection(self):
        """If no name is provided, it should be loaded from Basecamp."""
        self.project.name = ''
        self.project.detect_name()
        self.assertEqual("API Testing Project", self.project.name)

class DashboardUnitTests(BaseboardTestHelper):
    def create_dashboard(self, save=True, **kwargs):
        """Create a Dashboard object, using the optional kwargs. If save=False the object is returned without saving."""
        index = self.object_index()
        if not kwargs: kwargs = dict(name="Test Dashboard %s" % index, slug="test-dashboard-%s" % index)
        d = Dashboard(**kwargs)

        if not save: return d
        
        d.save()
        self.assert_(d.id) #Cheap validity check
        return d

    def test_str(self):
        d = self.create_dashboard(name="Test Dashboard", slug="test-dashboard")
        expected = "Test Dashboard"
        actual = str(d)

        self.assertEqual(actual, expected)

def runtests():
    import os
    os.system("python ./runtests.py")

if __name__ == "__main__":
    runtests()
