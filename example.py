
import pout


# our descriptor decorator
class Dec(object):
    def __new__(cls, *args, **kwargs):
        pout.v("__new__", args, kwargs)
        return super(Dec, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        pout.v("__init__", args, kwargs)

    def __set__(self, *args, **kwargs):
        pout.v("__set__", args, kwargs)



    def __get__(self, instance, klass):
        """
        having this method here turns the class into a descriptor used when there
        is no (...) on the decorator
        """
        pout.v("__get__", instance, klass)
        def wrapper(*args, **kwargs):
            return "__get__"
        return wrapper

    def __call__(self, *args, **kwargs):
        """call is used when there are (...) on the decorator"""
        pout.v("__call__", args, kwargs)

        def wrapper(*args, **kwargs):
            return "__call__"
        return wrapper


# the first state is decorated with no params
pout.b("@Dec")
@Dec
def foo(*args, **kwargs): pass
foo("func1", "func2")

# problem here is this is indistinguishable from @Dec
pout.b("@Dec(callback)")
def callback(*args, **kwargs): pass
@Dec(callback)
def foo(*args, **kwargs): pass
foo("func1", "func2")


pout.b(5)

# second state is decorated but no passed in params
pout.b("@Dec()")
@Dec()
def foo(*args, **kwargs): pass
foo()

# third state is decorated with passed in params
pout.b("@Dec(...)")
@Dec("dec1", "dec2")
def foo(*args, **kwargs): pass
foo()


