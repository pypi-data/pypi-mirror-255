class CachedProperty:
    def __init__(self, method):
        self.method = method
        self.name = method.__name__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.method(obj)
        setattr(obj, self.name, value)
        return value
