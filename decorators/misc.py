# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from .compat import *
from .base import FuncDecorator


class once(FuncDecorator):
    """run the decorated function only once for the given arguments

    :Example:
        @once
        def func(x):
            print("adding")
            return x + 1
        func(4) # prints "adding"
        func(10) # prints "adding"
        func(4) # returns 5, no print
        func(10) # returns 11, no print
    """
    def decorate(self, f, *once_args, **once_kwargs):
        def wrapped(*args, **kwargs):
            name = String(hash(f))
            if args:
                for a in args:
                    name += String(hash(a))

            if kwargs:
                for k, v in kwargs.items():
                    name += String(hash(k))
                    name += String(hash(v))

            try:
                ret = getattr(self, name)

            except AttributeError:
                ret = f(*args, **kwargs)
                setattr(self, name, ret)

            return ret
        return wrapped

