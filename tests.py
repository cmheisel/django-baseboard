import random

from django.test import TestCase

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
    os.system("django-admin.py test baseboard --verbosity=0")

if __name__ == "__main__":
    runtests()
