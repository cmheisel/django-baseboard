from django.db import models

from basecampreporting.project import Project as Basecamp

class Project(models.Model):
    """Represents a Basecamp-backed project"""
    slug = models.SlugField(unique=True)
    basecamp_id = models.IntegerField()
    basecamp_url = models.URLField(verify_exists=False)

    name = models.CharField(max_length=255, blank=True)    
    description = models.TextField(blank=True)
    
    Basecamp = Basecamp

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
        if not self.basecamp_id and self.basecamp_domain: return None
        self.name = self.basecamp_project.name
        return self.name

    @property
    def basecamp_project(self):
        if self._basecamp_project: return self._basecamp_project
        self._basecamp_project = self.BasecampProject()
    
    
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
