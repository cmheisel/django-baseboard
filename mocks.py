class TestSerializable(object):
    def __init__(self, **kwargs):
        self.data = kwargs
        for key, value in kwargs.items():
            self.__dict__[key] = value    

    def to_dict(self):
        return self.data

class TodoList(TestSerializable):
    pass

class TestBasecampProject(object):
    name = "Kobol's Last Gleaming"
    current_sprint = TodoList(name="Sprint 33 - Flee", sprint_number=33)
    
    def __init__(self, *args, **kwargs):
        pass
