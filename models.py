from django.db import models

class Project(models.Model):
    """Represents a Basecamp-backed project"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    project_id = models.IntegerField()
    description = models.TextField(blank=True)
    

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
