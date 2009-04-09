import datetime, pprint
import cPickle as pickle

from django.db import models

from basecampreporting.project import Project as BasecampProject

class Project(models.Model):
    """Represents a Basecamp-backed project"""
    slug = models.SlugField(unique=True)
    basecamp_url = models.URLField(verify_exists=False, unique=True)
    basecamp_id = models.IntegerField(unique=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    

    basecamp_updated_at = models.DateTimeField(editable=False, null=True)
    description = models.TextField(blank=True)
    summary_data = models.TextField(blank=True, editable=False)
    readable_summary = models.TextField(blank=True)
    
    BasecampProject = BasecampProject

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        self.detect_basecamp_id()
        self.detect_name()

        self.updated_at = datetime.datetime.now()
        if not self.id:
            self.created_at = datetime.datetime.now()
        
        super(Project, self).save(force_insert, force_update)

    def detect_basecamp_id(self):
        '''If project_url is set, it is parsed for the project_id.'''
        if not self.basecamp_url: return None
        parts = self.basecamp_url.split('/')
        try:
            id_string = parts[4]
        except IndexError:
            return None

        try:
            self.basecamp_id = int(id_string)
        except TypeError:
            return None

        return self.basecamp_id

    @property
    def basecamp_api_url(self):
        """Extracts domain from basecamp_url if set."""
        if not self.detect_basecamp_id(): return None

        parts = self.basecamp_url.split('/')
        try:
            api_url = "%s//%s/" % (parts[0], parts[2])
        except IndexError:
            return None
        
        return api_url

    def detect_name(self):
        """Fetches name from Basecamp."""
        if not self.basecamp_id and self.basecamp_url: return None
        self.name = self.basecamp_project.name
        return self.name

    @property
    def basecamp_project(self):
        if hasattr(self, '_basecamp_project'): return self._basecamp_project #Caching

        username, password = self.basecamp_credentials
        self._basecamp_project = self.BasecampProject(self.basecamp_api_url, self.basecamp_id, username, password)
        return self._basecamp_project

    @property
    def basecamp_credentials(self):
        from django.conf import settings
        return settings.BASEBOARD_CREDENTIALS[self.basecamp_api_url]

    @property
    def summary(self):
        if not self.summary_data: return {}
        if hasattr(self, '_summary_object_cache'): return self._summary_object_cache
        
        self._summary_object_cache = pickle.loads(self.summary_data)

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
        summary_data['backlogs'] = [ t.to_dict() for t in self.basecamp_project.backlogs.values() ]
        summary_data['backlogged_count'] = self.basecamp_project.backlogged_count
            
        self.readable_summary = pprint.pformat(summary_data)
        self.summary_data = pickle.dumps(summary_data)
        self.save()
    
    
class Dashboard(models.Model):
    """A collection of projects."""
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    projects = models.ManyToManyField(Project, related_name="dashboards")

    def __unicode__(self):
        return self.name
        

if __name__ == "__main__":
    import baseboard.tests
    tests.runtests()
