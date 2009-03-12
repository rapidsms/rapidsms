from rapidsms.router import Router

# a subclass of Router with all the moving parts replaced
class MockRouter (Router):
    def __init__ (self):
        Router.__init__(self)
        self.logged = [] 

    def log(self, *args):
        self.logged.append(args)
    
    def add_backend (self, backend):
        self.backends.append(backend)

    def add_app (self, app):
        self.apps.append(app)

    def start (self):
        self.running = True
        self.start_all_backends()
        self.start_all_apps()

    def stop (self):
        self.running = False
        self.stop_all_backends()
