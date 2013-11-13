import functools
import inspect

__version__ = "0.1"

class Decorator(object):
    """
    A decorator class that you can be extended that allows you to do normal decorators
    with no arguments, or a decorator with arguments

    May be invoked as a simple, argument-less decorator (i.e. `@decorator`) or
    with arguments customizing its behavior (e.g. `@decorator(*args, **kwargs)`).

    To create your own decorators, just extend this class and override the decorate()
    method, the decorate() method should return a method that can call the passed in func
    at some point

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
    wrapped_class = False
    wrapped_instance = False

    def __new__(cls, *args, **kwargs):
        instance = super(Decorator, cls).__new__(cls)

        if instance.is_wrapped_arg(*args, **kwargs):
            instance.set_wrapped(args[0])
            args = ()
            instance.args = args

        else:
            instance.wrapped = None

        instance.args = args
        instance.kwargs = kwargs

        # here we do some magic stuff to return the class back in case this is a
        # class decorator, we do this so we don't wrap the class, thus causing
        # things like isinstance() checks to fail, and also not making class
        # variables available
        if instance.wrapped_class:
            if instance.wrapped_instance:
                decorate_instance = instance
                klass_instance = instance.decorate_class(
                    instance.wrapped,
                    *instance.args,
                    **instance.kwargs
                )

                class ChildClass(klass_instance):
                    def __init__(self, *args, **kwargs):
                        super(ChildClass, self).__init__(*args, **kwargs)
                        decorate_instance.decorate_instance(
                            self, *decorate_instance.args, **decorate_instance.kwargs
                        )

                instance = ChildClass
                instance.__name__ = klass_instance.__name__
                instance.__module__ = klass_instance.__module__
                # for some reason you can't update a __doc__ on a class
                # http://bugs.python.org/issue12773

            else:
                instance = instance.decorate_class(instance.wrapped, *instance.args, **instance.kwargs)

        return instance

    def is_wrapped_arg(self, *args, **kwargs):
        ret = False
        if len(args) == 1 and len(kwargs) == 0:
            if inspect.isfunction(args[0]) \
            or isinstance(args[0], type) \
            or isinstance(args[0], FuncDecorator):
                ret = True

        return ret

    def set_wrapped(self, wrapped):
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
        is no (...) on the decorator
        """
        def wrapper(*args, **kwargs):
            ret = self.decorate_func(self.wrapped, *self.args, **self.kwargs)(instance, *args, **kwargs)
            return ret
        return wrapper

    def __call__(self, *args, **kwargs):
        """call is used when there are (...) on the decorator"""
        ret = None
        invoke = True
        if not self.wrapped:
            self.set_wrapped(args[0])
            args = ()
            invoke = False

        if self.wrapped_func:
            ret = self.decorate_func(self.wrapped, *self.args, **self.kwargs)

        elif self.wrapped_class:
            ret = self.decorate_class(self.wrapped, *self.args, **self.kwargs)

        else:
            raise ValueError("wrapped is not a class or a function")

        if invoke:
            ret = ret(*args, **kwargs)

        if self.wrapped_instance:
            self.decorate_instance(ret, *self.args, **self.kwargs)

        return ret

    def decorate_func(self, func, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return a
        function that calls self.func

        func -- callback -- the function being decorated
        decorator_args -- tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        decorator_kwargs -- dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        raise RuntimeError("decorator {} does not support function decoration".format(self.__class__.__name__))
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def decorate_class(self, klass, *decorator_args, **decorator_kwargs):
        raise RuntimeError("decorator {} does not support class decoration".format(self.__class__.__name__))
        return klass

    def decorate_instance(self, instance, *decorator_args, **decorator_kwargs):
        raise RuntimeError("decorator {} does not support instance decoration".format(self.__class__.__name__))
        return instance


class InstanceDecorator(Decorator):
    wrapped_instance = True

    def decorate(self, instance, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return an
        instance of a class

        instance -- class() -- the class instance being decorated
        decorator_args -- tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        decorator_kwargs -- dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        return instance

    def decorate_instance(self, *args, **kwargs):
        return self.decorate(*args, **kwargs)

    def decorate_class(self, klass, *decorator_args, **decorator_kwargs):
        return klass


class ClassDecorator(Decorator):
    def decorate(self, klass, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return a
        class object

        klass -- class -- the class being decorated
        decorator_args -- tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        decorator_kwargs -- dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        return klass

    def decorate_class(self, *args, **kwargs):
        return self.decorate(*args, **kwargs)


class FuncDecorator(Decorator):
    def decorate(self, func, *decorator_args, **decorator_kwargs):
        """
        override this in a child class with your own logic, it must return a
        function that calls self.func

        func -- callback -- the function being decorated
        decorator_args -- tuple -- the arguments passed into the decorator (eg, @dec(1, 2))
        decorator_kwargs -- dict -- the named args passed into the decorator (eg, @dec(foo=1))
        """
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def decorate_func(self, *args, **kwargs):
        return self.decorate(*args, **kwargs)


