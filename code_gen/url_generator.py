from code_gen.code_generator import CodeGenerator

class UrlEntry:
    def __init__(self, path, view, name):
        self.path = path
        self.view = view
        self.name = name           

class UrlGenerator(CodeGenerator):
    insertion_index = 0
    
    def __init__(self, urls):
        self._urls = urls
        super().__init__()
        
    
        
