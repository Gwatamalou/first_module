class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class MyClass1(metaclass=SingletonMeta): ...

a1 = MyClass1()
a2 = MyClass1()

assert a1 is a2

"""
==================================
"""

class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

s1 = Singleton()
s2 = Singleton()

assert s1 is s2


"""
==================================
"""

from singltoneImport import singleton_import

x1 = singleton_import
x2 = singleton_import

assert s1 is s2


