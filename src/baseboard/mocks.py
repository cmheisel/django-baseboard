import datetime

class TestSerializable(object):
    def __init__(self, **kwargs):
        self.data = kwargs
        for key, value in kwargs.items():
            self.__dict__[key] = value    

    def to_dict(self):
        return self.data

class TodoList(TestSerializable):
    pass

class Milestone(TestSerializable):
    pass

class TestBasecampProject(object):
    name = "Kobol's Last Gleaming"
    current_sprint = TodoList(name="Sprint 33 - Flee", sprint_number=33)
    upcoming_sprints = [TodoList(name="Sprint 34 - Water", sprint_number=34), ]
    late_milestones = []
    upcoming_milestones = [ Milestone(name="Bastille Day", deadline=datetime.datetime(3000, 1, 1)), ]
    previous_milestones = []
    backlogs = {}
    backlogged_count = 0
    last_changed_on = datetime.datetime.now() - datetime.timedelta(hours=6, minutes=1)
    
    def __init__(self, *args, **kwargs):
        pass

if __name__ == "__main__":
    import os
    os.system("~/local/bin/python runtests.py")
