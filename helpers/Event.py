class Event():
    def __init__(self):
        self.subscribers = []
    
    def Subscribe(self, callback):
        self.subscribers.append(callback)

    def notify(self, *args, **kwargs):
        for subscriber in self.subscribers:
            subscriber(*args, **kwargs)