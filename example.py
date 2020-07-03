# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import inspect
import sys

import pout




class DecType(type):
    def __getattribute__(self, k):
        return super(DecType, self).__getattribute__(k)


# our descriptor decorator
class Dec(object):

    __metaclass__ = DecType

    def __new__(cls, *args, **kwargs):
        pout.v("__new__", args, kwargs)

        #frame = inspect.currentframe()
        #frames = inspect.getouterframes(frame)
        #pout.v(frame, frames)


        return super(Dec, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        pout.v("__init__", args, kwargs)

    def __set__(self, *args, **kwargs):
        pout.v("__set__", args, kwargs)

    def __getattribute__(self, k):
        pout.v(k)
        return super(Dec, self).__getattribute__(k)

    def __get__(self, *args, **kwargs):
        """
        having this method here turns the class into a descriptor used when there
        is no (...) on the decorator
        """
        pout.v("__get__", args, kwargs)
        def wrapper(*args, **kwargs):
            pout.v("wrapper", args, kwargs)
        return wrapper

    def __call__(self, *args, **kwargs):
        """call is used when there are (...) on the decorator"""
        pout.v("__call__", args, kwargs)
        #pout.v(vars(self))
        #frame = inspect.currentframe()
        #frames = inspect.getouterframes(frame)
        #pout.v(frames[1:])

        def wrapper(*args, **kwargs):
            pout.v("wrapper", args, kwargs)
        return wrapper


# the first state is decorated with no params
pout.b("@Dec")
@Dec
def foo(*args, **kwargs): pass

pout.b()
foo("func1", "func2")


# problem here is this is indistinguishable from @Dec
pout.b("@Dec(callback)")
def callback(*args, **kwargs): pass
@Dec(callback)
def foo(*args, **kwargs): pass
pout.v("defined")
foo("func1", "func2")

pout.b(5)

pout.b("Class @Dec")
class Foo(object):
    @Dec
    def foo(*args, **kwargs): pass
pout.v("defined")
f = Foo()
f.foo("method1", "method2")

pout.b("Class @Dec(callback)")
def callback(*args, **kwargs): pass
class Foo(object):
    @Dec(callback)
    def foo(*args, **kwargs): pass
pout.v("defined")
f = Foo()
f.foo("method1", "method2")


pout.b("multiline @Dec(callback)")
@Dec(
    callback
)
def foo(*args, **kwargs): pass

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


