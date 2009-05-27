
import datetime, pprint
import cPickle as pickle

import feedparser

from django.db import models
from django.template.defaultfilters import slugify

from basecampreporting.project import Project as BasecampProject
#Random comment

class InvalidBasecampUrl(Exception):
    pass

class MissingCredentials(Exception):
    pass

class RSSFeed(models.Model):
    """Represents an RSS feed."""
    url = models.URLField(verify_exists=True, unique=True, max_length=255)
    name = models.CharField(max_length=255)
    feed_info = models.TextField(blank=True, editable=False)
    feed_contents = models.TextField(blank=True, editable=False)
    parsed_at = models.DateTimeField(editable=False, null=True) 
    update_error = models.TextField(blank=True)

    feedparser = feedparser

    class Meta:
        verbose_name = "RSS Feed"


    def update_feed(self, save=True):
        parsed = self.feedparser.parse(self.url)
        self.feed_contents = pickle.dumps(parsed['entries'])

        info = {}
        for key, value in parsed.items():
            if key != 'entries':
                info[key] = value
        try:
            self.feed_info = pickle.dumps(info)
            self.parsed_at = datetime.datetime.now()
        except pickle.UnpickleableError, err:
            self.update_error = str(err)
        if save:
            self.save()

    @property
    def contents(self):
        if not self.feed_contents:
            return {}
        return pickle.loads(str(self.feed_contents))

    @property
    def info(self):
        if not self.feed_contents:
            return {} 
        return pickle.loads(str(self.feed_info))

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        if self.info and self.contents:
            pass #We've been parsed at least once
        else:
            self.update_feed(save=False)

        if not self.name:
            self.name = self.info['feed']['title']
        super(RSSFeed, self).save(force_insert, force_update)

class Project(models.Model):
    """Represents a Basecamp-backed project"""
    slug = models.SlugField(unique=True, blank=True, help_text="This will be prefilled from the project's name if left blank.")
    basecamp_url = models.URLField(verify_exists=False, unique=True, help_text="Example: https://ajcprojects.updatelog.com/projects/2404439/project/log")
    basecamp_id = models.IntegerField(unique=True, blank=True)
    name = models.CharField(max_length=255, blank=True, help_text="This will be prefilled from the project if left blank.")
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
     

    basecamp_updated_at = models.DateTimeField(editable=False, null=True)
    description = models.TextField(blank=True, help_text="A brief summary of the project and its goals.")
    summary_data = models.TextField(blank=True, editable=False)
    readable_summary = models.TextField(blank=True)
    update_error = models.TextField(blank=True)

    feeds = models.ManyToManyField(RSSFeed, related_name="projects", blank=True)

    BasecampProject = BasecampProject

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        if not self.basecamp_id:
            self.basecamp_id = Project.extract_basecamp_id(self.basecamp_url)
        
        self.detect_name()

        if not self.slug:
            self.slug = slugify("%s-%s" % (self.basecamp_id, self.name))

        self.updated_at = datetime.datetime.now()
        if not self.id:
            self.created_at = datetime.datetime.now()

        if not self.summary_data: self.update_summary()
        super(Project, self).save(force_insert, force_update)

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), { 'slug': self.slug })

    @classmethod
    def extract_basecamp_id(cls, basecamp_url):
        parts = basecamp_url.split('/')
        try:
            id_string = parts[4]
        except IndexError:
            return None

        try:
            basecamp_id = int(id_string)
        except TypeError:
            return None
        return basecamp_id

    @classmethod
    def extract_basecamp_api_url(cls, url):
        parts = url.split('/')
        try:
            api_url = "%s//%s/" % (parts[0], parts[2])
        except IndexError:
            return None
        return api_url

    @classmethod
    def get_credentials_for(cls, api_url):
        from django.conf import settings
        try:
            return settings.BASEBOARD_CREDENTIALS[api_url]
        except KeyError:
            return None
    
    @property
    def project_url(self):
        """Returns the Basecamp project homepage URL for a project.
        (Because users can enter any URL from a project 
        as self.basecamp_url)"""
        
        base_url = Project.extract_basecamp_api_url(self.basecamp_url)
        return "%sprojects/%s/project/log" % (base_url, self.basecamp_id)

    @property
    def basecamp_project(self):
        #if hasattr(self, '_basecamp_project'): return self._basecamp_project #Caching

        api_url = Project.extract_basecamp_api_url(self.basecamp_url)
        username, password = Project.get_credentials_for(api_url)

        return self.BasecampProject(api_url, self.basecamp_id, username, password)
        #return self._basecamp_project

    def detect_name(self):
        """Fetches name from Basecamp."""
        if not self.name:
            self.name = self.basecamp_project.name
        return self.name

    @property
    def summary(self):
        if not self.summary_data: return {}
        if hasattr(self, '_summary_object_cache'): return self._summary_object_cache
        
        self._summary_object_cache = pickle.loads(str(self.summary_data))

        return self._summary_object_cache

    def update_summary(self):
        """Makes network calls to Basecamp to update
        the summary information."""
        self.basecamp_updated_at = datetime.datetime.now()

        summary_data = {}

        if self.basecamp_project.current_sprint:
            summary_data['current_sprint'] = self.basecamp_project.current_sprint.to_dict()

        summary_data['upcoming_sprints'] = [ s.to_dict() for s in self.basecamp_project.upcoming_sprints ]
        summary_data['late_milestones'] = [ m.to_dict() for m in self.basecamp_project.late_milestones[0:3] ]
        summary_data['upcoming_milestones'] = [ m.to_dict() for m in self.basecamp_project.upcoming_milestones[0:3] ]
        summary_data['previous_milestones'] = [ m.to_dict() for m in self.basecamp_project.previous_milestones[0:3] ]
        summary_data['backlogs'] = [ t.to_dict() for t in self.basecamp_project.backlogs.values() ]
        summary_data['backlogged_count'] = self.basecamp_project.backlogged_count
        summary_data['last_changed_on'] = self.basecamp_project.last_changed_on
            
        self.readable_summary = pprint.pformat(summary_data)
        self.summary_data = pickle.dumps(summary_data)
        self.save()

    def is_late(self):
        """Returns true if there's a late milestone."""
        try:
            if self.summary['late_milestones']: return True
        except KeyError:
            pprint.pprint(self.summary)
        return False

    def is_stale(self):
        """Returns true if the basecamp project hasn't been updated in 3 days."""
        threshold = datetime.datetime.now() - datetime.timedelta(days=3)
        if threshold > self.summary['last_changed_on']: return True
        return False
    
class Dashboard(models.Model):
    """A collection of projects."""
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    projects = models.ManyToManyField(Project, related_name="dashboards")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('dashboard_detail', [], { 'slug': self.slug })
    
if __name__ == "__main__":
    from baseboard import tests
    tests.runtests()
