class TestBasecampProject(object):
    name = "Kobol's Last Gleaming"
    
    def __init__(self, *args, **kwargs):
        pass

class TestSerializable(object):
    def __init__(self, initial_params={}):
        self.data = initial_params
        for key, value in initial_params.items():
            self.__dict__[key] = value

class TestTodoList(TestSerializable):
    pass
    
    
