# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from .compat import *
from .base import FuncDecorator


class classproperty(property):
    """
    allow a readonly class property to exist on a class with a similar interface
    to the built-in property decorator

    NOTE -- because of Python's architecture, this can only be read only, you can't
        create a setter or deleter

    :Example:
        class Foo(object):
            @classproperty
            def bar(cls):
                return 42
        Foo.bar # 42

    http://stackoverflow.com/questions/128573/using-property-on-classmethods
    http://stackoverflow.com/questions/5189699/how-can-i-make-a-class-property-in-python
    https://stackoverflow.com/a/38810649/5006
    http://docs.python.org/2/reference/datamodel.html#object.__setattr__
    https://stackoverflow.com/a/3203659/5006
    """
    def __init__(self, fget, doc=None):
        super(classproperty, self).__init__(fget, doc=doc)

    def __get__(self, instance, instance_class=None):
        return self.fget(instance_class)

    def setter(self, fset):
        raise TypeError("classproperty is readonly due to python's architecture")

    def deleter(self, fdel):
        raise TypeError("classproperty is readonly due to python's architecture")


class property(FuncDecorator):
    """A replacement for the built-in @property that enables extra functionality

    See http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    see https://docs.python.org/2/howto/descriptor.html
    see http://stackoverflow.com/questions/17330160/python-how-does-the-property-decorator-work
    see https://docs.python.org/2/howto/descriptor.html

    :Example:
        # make this property memoized (cached)
        class Foo(object):
            @property(cached="_bar")
            def bar(self):
                return 42 # will be cached to self._bar
        f = Foo()
        f.bar # 42
        f._bar # 42

    Options you can pass into the decorator to customize the property

        * allow_empty -- boolean (default True) -- False to not cache empty values (eg, None, "")
        * cached -- string, pass in the variable name (eg, "_foo") that the value
            returned from the getter will be cached to
        * setter -- string, set this to variable name (similar to cached) if you want the decorated
            method to act as the setter instead of the getter, this will cause a default
            getter to be created that just returns variable name
        * deleter -- string, same as setter, but the descorated method will be the deleter and default
            setters and getters will be created
    """
    def decorate(self, method, *args, **kwargs):
        if "setter" in kwargs:
            ret = self.setter(method)

        elif "deleter" in kwargs:
            ret = self.deleter(method)

        else:
            ret = self.getter(method)

        return ret

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        self.getter(fget)
        self.setter(fset)
        self.deleter(fdel)

        if doc:
            self.__doc__ = doc

        self.name = ""
        for k in ["cached", "cache", "setter", "deleter"]:
            if k in kwargs:
                self.name = kwargs[k]
                break

        self.cached = True if self.name else False
        if "allow_empty" in kwargs:
            if self.cached:
                self.allow_empty = kwargs.pop('allow_empty', True)
            else:
                raise ValueError("Cannot set allow_empty with cached")

    def get_value(self, instance):
        if self.fget:
            try:
                return self.fget(instance)

            except AttributeError as e:
                # if there is a __getattr__ then this AttributeError could get
                # swallowed and so let's reraise it as a ValueError
                # fixes https://github.com/Jaymon/decorators/issues/4
                if hasattr(instance, "__getattr__"):
                    exc_info = sys.exc_info()
                    reraise(ValueError, e, exc_info[2])

                else:
                    raise

        else:
            raise AttributeError("Unreadable attribute")

    def __get__(self, instance, instance_class=None):
        # if there is no instance then they are requesting the property from the class
        if instance is None:
            return self

        if self.cached:
            if self.name in instance.__dict__:
                value = instance.__dict__[self.name]
                if not value and not self.allow_empty:
                    value = self.get_value(instance)
                    if value or self.allow_empty:
                        self.__set__(instance, value)

            else:
                value = self.get_value(instance)
                if value or self.allow_empty:
                    self.__set__(instance, value)

        else:
            value = self.get_value(instance)

        return value

    def __set__(self, instance, value):
        if self.cached:
            if self.fset:
                self.fset(instance, value)

            else:
                instance.__dict__[self.name] = value

        else:
            if self.fset is None:
                raise AttributeError("Can't set attribute")

            self.fset(instance, value)

    def __delete__(self, instance):
        if self.cached:
            if self.fdel:
                self.fdel(instance)

            else:
                if self.name in instance.__dict__:
                    instance.__dict__.pop(self.name, None)

                else:
                    raise AttributeError("Can't delete attribute")

        else:
            if self.fdel:
                self.fdel(instance)
            else:
                raise AttributeError("Can't delete attribute")

    def getter(self, fget):
        self.fget = fget
        return self

    def setter(self, fset):
        self.fset = fset
        return self

    def deleter(self, fdel):
        self.fdel = fdel
        return self


class xproperty(object):
    """A memoized @property that is only evaluated once, and then stored at _property
    and retrieved from there unless deleted, in which case this would be called
    again and stored in _property again.
    See http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    see https://docs.python.org/2/howto/descriptor.html
    see http://stackoverflow.com/questions/17330160/python-how-does-the-property-decorator-work
    see https://docs.python.org/2/howto/descriptor.html
    options you can use to further customize the property
    read_only -- boolean (default False) -- set to de-activate set and del methods
    allow_empty -- boolean (default True) -- False to not cache empty values (eg, None, "")
    setter -- boolean -- set this to true if you want the decorated method to act as the setter
        instead of the getter, this will cause a default getter to be created that just returns
        _name (you should set self._name in your setter)
    deleter -- boolean -- same as setter, set to True to have the method act as the deleter
    """
    def __init__(self, *args, **kwargs):
        self.allow_empty = kwargs.get('allow_empty', True)
        self.has_setter = kwargs.get('setter', False)
        self.has_deleter = kwargs.get('deleter', False)

        has_no_write = not self.has_setter and not self.has_deleter
        self.has_getter = kwargs.get('getter', has_no_write)

        # mutually exclusive to having defined a setter or deleter
        self.read_only = kwargs.get('read_only', False) and has_no_write

        if args:
            if isinstance(args[0], bool):
                self.read_only = args[0]

            else:
                # support _property(fget, fset, fdel, desc) also
                total_args = len(args)
                self.set_method(args[0])
                if total_args > 1:
                    self.setter(args[1])
                if total_args > 2:
                    self.deleter(args[2])
                if total_args > 3:
                    self.__doc__ = args[3]

        # support _property(fget=getter, fset=setter, fdel=deleter, doc="")
        if "fget" in kwargs:
            self.set_method(kwargs["fget"])
        if "fset" in kwargs:
            self.setter(kwargs["fset"])
        if "fdel" in kwargs:
            self.deleter(kwargs["fdel"])
        if "doc" in kwargs:
            self.__doc__ = kwargs["doc"]

    def set_method(self, method):
        self.fget = method if self.has_getter else self.default_get
        self.fset = method if self.has_setter else self.default_set
        self.fdel = method if self.has_deleter else self.default_del
        self.__doc__ = method.__doc__
        self.__name__ = method.__name__
        self.name = '_{}'.format(self.__name__)

    def __call__(self, *args, **kwargs):
        if args:
            self.set_method(args[0])

        return self

    def __get__(self, instance, cls):
        # return the cached value if it exists
        val = None
        name = self.name
        if name in instance.__dict__:
            val = instance.__dict__[name]

        else:
            try:
                val = self.fget(instance)
                if val or self.allow_empty:
                    # We don't do fset here because that causes unexpected bahavior
                    # if you ever override the setter, causing the setter to be fired
                    # every time the getter is called, which confused me for about
                    # an hour before I figured out what was happening
                    self.default_set(instance, val)

            except Exception:
                # make sure no value gets set no matter what
                instance.__dict__.pop(name, None)
                raise

        return val

    def default_get(self, instance):
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError("can't get attribute {}".format(self.__name__))

    def default_set(self, instance, val):
        instance.__dict__[self.name] = val

    def __set__(self, instance, val):
        if self.read_only:
            raise AttributeError("can't set attribute {}".format(self.__name__))

        if val or self.allow_empty:
            self.fset(instance, val)

    def default_del(self, instance):
        instance.__dict__.pop(self.name, None)

    def __delete__(self, instance, *args):
        if self.read_only:
            raise AttributeError("can't delete attribute {}".format(self.__name__))

        self.fdel(instance)

    def getter(self, fget):
        self.fget = fget
        self.has_getter = True
        return self

    def setter(self, fset):
        self.fset = fset
        self.has_setter = True
        return self

    def deleter(self, fdel):
        self.fdel = fdel
        self.has_deleter = True
        return self

