from django.db import models

from basecampreporting.project import Project as Basecamp

class Project(models.Model):
    """Represents a Basecamp-backed project"""
    slug = models.SlugField(unique=True)
    basecamp_id = models.IntegerField()
    basecamp_domain = models.CharField(max_length=80)

    basecamp_url = models.URLField(verify_exists=False, blank=True)

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

    def detect_basecamp_domain(self):
        """Extracts domain from basecamp_url if set."""
        if not self.detect_basecamp_id(): return None

        parts = self.basecamp_url.split('/')
        try:
            domain_string = parts[2]
            self.basecamp_domain = domain_string
        except IndexError:
            print parts
            return None
        
        return self.basecamp_domain
    
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
