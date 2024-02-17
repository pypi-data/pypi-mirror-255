class Singleton(object):
    _inited = False
    
    _instance_ = {}
    def __new__(cls, *args, **kwargs):
        key = str(cls) + str(args) + str(kwargs)
        if key not in cls._instance_:
            cls._instance_[key] = super().__new__(cls)
            cls._instance_[key].__key__ = key
        return cls._instance_[key]
    
    def need_init(self):
        return not self._inited

    def __init__(self, *args, **kwargs):
        pass

    def dispose(self):
        print('collect memory instance: {}'.format(self.__key__))
        if self.__key__ in self._instance_:
            del self._instance_[self.__key__]
    