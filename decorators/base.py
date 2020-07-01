# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import functools
import inspect
import re


__version__ = "0.1.1"


class Decorator(object):
    """
    A decorator class that you can be extended that allows you to do normal decorators
    with no arguments, or a decorator with arguments

    May be invoked as a simple, argument-less decorator (eg, `@decorator`) or
    with arguments customizing its behavior (eg,`@decorator(*args, **kwargs)`).

    To create your own decorators, just extend this class and override the decorate_func()
    method to decorate functions/methods and/or the decorate_class() method to decorate
    classes.

    based off of the task decorator in Fabric
    https://github.com/fabric/fabric/blob/master/fabric/decorators.py#L15

    with modifications inspired by --
    https://wiki.python.org/moin/PythonDecoratorLibrary#Class_method_decorator_using_instance
    https://wiki.python.org/moin/PythonDecoratorLibrary#Creating_decorator_with_optional_arguments

    other links --
    http://pythonconquerstheuniverse.wordpress.com/2012/04/29/python-decorators/
    http://stackoverflow.com/questions/739654/
    http://stackoverflow.com/questions/666216/decorator-classes-in-python
    """
    wrapped_func = False
    """this decorator is wrapping an instance, auto-discovered"""

    wrapped_class = False
    """this decorator is wrapping a class, auto-discovered"""

    required_args = False
    """set this to True in child if the decorator requires arguments (eg, @dec(...))"""

    def __new__(cls, *args, **kwargs):
        instance = super(Decorator, cls).__new__(cls)

        instance.create_args = args
        instance.create_kwargs = kwargs

        if instance.is_wrapped_arg(*args, **kwargs):
            instance.set_wrapped(args[0])
            args = ()

        else:
            instance.wrapped = None

        instance.args = args
        instance.kwargs = kwargs

        # here we do some magic stuff to return the class back in case this is a
        # class decorator, we do this so we don't wrap the class, thus causing
        # things like isinstance() checks to fail, and also not making class
        # variables available
        if instance.wrapped_class:
            try:
                instance = instance.decorate_class(
                    instance.wrapped,
                    *instance.args,
                    **instance.kwargs
                )
            except TypeError as e:
                # recover from is_wrapped_arg misclassifying the call
                # NOTE -- this is super hacky
                e_msg = str(e)
                if "arguments" in e_msg and "takes" in e_msg \
                    or ("argument" in e_msg and "missing" in e_msg):
                    instance.wrapped = None
                    instance.args = instance.create_args
                    instance.kwargs = instance.create_kwargs
                else:
                    raise

        return instance

    def is_wrapped_arg(self, *args, **kwargs):
        """decide if this decorator was called with arguments (eg, @dec(...)) or
        without (eg, @dec) so we can take the correct path when the decorator is
        invoked

        for the most part this works except for the case where you have one callback
        or class as the only passed in method to the decorator (eg, @dec(lambda x: x)),
        you can get around it by using named arguments (eg, @dec(callback=lambda x: x))
        or by setting required_args class property to True in your child decorator,
        otherwise this will try and autodiscover and have to recover when the
        decorator is actually invoked. I wracked my brain trying to figure out a
        better way to do this and I couldn't come up with anything and after the
        hours I've spent on it I'm just not sure there is a way to really know

        :param *args: any positional values passed into __new__ or __call__
        :param **kwargs: any named values passed into __new__ or __call__
        :returns: boolean
        """
        ret = False
        if len(args) == 1 and len(kwargs) == 0:
            #pout.v(args, self, isinstance(args[0], type), isinstance(args[0], FuncDecorator))
            ret = inspect.isfunction(args[0]) \
                or isinstance(args[0], type) \
                or isinstance(args[0], Decorator)
            if ret:
                ret = not self.required_args
#                 if ret:
#                     frames = inspect.getouterframes(inspect.currentframe())
#                     if len(frames) >= 3:
#                         dec_frame = frames[2]
#                         lines = "".join(dec_frame[4]).strip()
#                         # we have 3 possibilities here:
#                         # 1) @dec
#                         # 2) @dec(...)
#                         # 3) something else
#                         # this will return True for 1 and 3
#                         if re.match(r"^@", lines):
#                             ret = "(" not in lines

        return ret

    def set_wrapped(self, wrapped):
        """This will decide what wrapped is and set .wrapped_func or .wrapped_class
        accordingly

        :param wrapped: either a function or class
        """
        self.wrapped = wrapped
        functools.update_wrapper(self, self.wrapped, updated=())
        self.wrapped_func = False
        self.wrapped_class = False

        if inspect.isroutine(wrapped):
            self.wrapped_func = True

        elif isinstance(wrapped, type):
            self.wrapped_class = True

    def __get__(self, instance, klass):
        """
        having this method here turns the class into a descriptor used when there
        is no (...) on the decorator, this is only called when the decorator is on
        a method, it won't be called when the decorator is on a non class method
        (ie, just a normal function)
        """
        def wrapper(*args, **kwargs):
            ret = self.decorate_func(self.wrapped, *self.args, **self.kwargs)(instance, *args, **kwargs)
            return ret
        return wrapper

    def __call__(self, *args, **kwargs):
        """call is used when there are (...) on the decorator or when there are no (...)
        and the actual wrapped thing (function/method/class) is called"""
        call_args = args
        call_kwargs = kwargs
        ret = None
        invoke = True
        if not self.wrapped:
            self.set_wrapped(args[0])
            args = ()
            invoke = False

        try:

            if self.wrapped_func:
                ret = self.decorate_func(self.wrapped, *self.args, **self.kwargs)

            elif self.wrapped_class:
                ret = self.decorate_class(self.wrapped, *self.args, **self.kwargs)

            else:
                raise ValueError("wrapped is not a class or a function")

        except TypeError as e:
            # recover from is_wrapped_arg misclassifying the call
            # NOTE -- this is super hacky
            e_msg = str(e)
            if "arguments" in e_msg and "takes" in e_msg \
                or ("argument" in e_msg and "missing" in e_msg):
                self.args = self.create_args
                self.kwargs = self.create_kwargs
                self.wrapped = None
                ret = self.__call__(*call_args, **call_kwargs)

            else:
                raise

        else:
            if invoke:
                ret = ret(*args, **kwargs)

        return ret

    def decorate_func(self, func, *decorator_args, **decorator_kwargs):
        """override this in a child class with your own logic, it must return a
        function that calls self.func

        :param func: callback -- the function being decorated
        :param decorator_args: tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        :param decorator_kwargs: dict -- the named args passed into the decorator (eg, @dec(foo=1))
        :returns: the wrapped func with our decorator func
        """
        raise RuntimeError("decorator {} does not support function decoration".format(self.__class__.__name__))
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def decorate_class(self, klass, *decorator_args, **decorator_kwargs):
        """override this in a child class with your own logic, it must return a
        function that returns klass or the like

        :param klass: the class object that is being decorated
        :param decorator_args: tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        :param decorator_kwargs: dict -- the named args passed into the decorator (eg, @dec(foo=1))
        :returns: the wrapped class
        """
        raise RuntimeError("decorator {} does not support class decoration".format(self.__class__.__name__))
        return klass


class InstanceDecorator(Decorator):
    """only decorate instances of a class"""
    def decorate(self, instance, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return an
        instance of a class

        :param instance: class() -- the class instance being decorated
        :param decorator_args: tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        :param decorator_kwargs: dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        return instance

    def decorate_class(self, klass, *decorator_args, **decorator_kwargs):
        """where the magic happens, this wraps a class to call our decorate method
        in the init of the class
        """
        class ChildClass(klass):
            def __init__(slf, *args, **kwargs):
                super(ChildClass, slf).__init__(*args, **kwargs)
                self.decorate(
                    slf, *decorator_args, **decorator_kwargs
                )

        decorate_klass = ChildClass
        decorate_klass.__name__ = klass.__name__
        decorate_klass.__module__ = klass.__module__
        # for some reason you can't update a __doc__ on a class
        # http://bugs.python.org/issue12773

        return decorate_klass


class ClassDecorator(Decorator):
    """only decorate a class"""
    def decorate(self, klass, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return a
        class object

        :param klass: class -- the class being decorated
        :param decorator_args: tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        :param decorator_kwargs: dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        return klass

    def decorate_class(self, *args, **kwargs):
        return self.decorate(*args, **kwargs)


class FuncDecorator(Decorator):
    """only decorate functions/methods"""
    def decorate(self, func, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return a
        function that calls self.func

        :param func: callback -- the function being decorated
        :param decorator_args: tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        :param decorator_kwargs: dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def decorate_func(self, *args, **kwargs):
        return self.decorate(*args, **kwargs)

