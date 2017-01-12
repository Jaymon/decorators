from unittest import TestCase

import decorators
from decorators import FuncDecorator, ClassDecorator, InstanceDecorator


class InstanceDecoratorTest(TestCase):
    def test_on_instance(self):
        class dec(InstanceDecorator):
            def decorate(self, instance, *dec_a, **dec_kw):
                if dec_a:
                    instance.val = dec_a[0]
                else:
                    instance.val = 2

                return instance

        @dec
        class IDFoo(object): 
            """this is the doc"""
            val = 1
            def bar(self): return self.val

        f = IDFoo
        self.assertTrue(issubclass(f, IDFoo))
        f = IDFoo()
        self.assertTrue(isinstance(f, IDFoo))
        self.assertEqual(2, f.bar())
        self.assertEqual(2, f.val)
        self.assertEqual(1, f.__class__.val)
        self.assertEqual(1, IDFoo.val)

        self.assertTrue(isinstance(f, IDFoo))

        @dec(5)
        class IDFoo2(object): 
            val = 1
            def __init__(self): pass
            def bar(self): return self.val

        f = IDFoo2
        self.assertTrue(issubclass(f, IDFoo2))
        f = IDFoo2()
        self.assertTrue(isinstance(f, IDFoo2))
        self.assertEqual(5, f.bar())
        self.assertEqual(5, f.val)


class ClassDecoratorTest(TestCase):

    def test_on_class(self):
        class dec(decorators.ClassDecorator):
            def decorate(self, klass, *dec_a, **dec_kw):
                if dec_a:
                    klass.val = dec_a[0]
                else:
                    klass.val = 1

                return klass

        @dec
        class CDFoo(object): 
            def __init__(self, *a, **kw): self.vals = a
            def bar(self): return self.val
        f = CDFoo(1, 2, 3)
        r = f.bar()
        self.assertTrue(isinstance(f, CDFoo))
        self.assertEqual(1, r)
        self.assertEqual((1, 2, 3), f.vals)

        @dec(5)
        class CDFoo2(object): 
            def __init__(self, *a, **kw): self.vals = a
            def bar(self): return self.val
        f = CDFoo2(4, 5, 6)
        r = f.bar()
        self.assertTrue(isinstance(f, CDFoo2))
        self.assertEqual(5, r)
        self.assertEqual((4, 5, 6), f.vals)

    def test_callback_param_explicit(self):
        class cbp(ClassDecorator):
            required_args = True
            def decorate(self, klass, oklass):
                return klass

        class Che(object): pass

        @cbp(Che)
        class Bar(object): pass

        b = Bar() # this shouldn't error, if it does we failed

    def test_callback_param_auto(self):
        class cbp(ClassDecorator):
            def decorate(self, klass, oklass):
                return klass

        class Che(object): pass

        @cbp(Che)
        class Bar(object): pass

        b = Bar() # this shouldn't error, if it does we failed

class FuncDecoratorTest(TestCase):
    def test_default_value(self):
        class dv(FuncDecorator):
            def decorate(self, func, bar=2):
                def decorated(*args, **kwargs):
                    return func(bar, *args, **kwargs)
                return decorated

        @dv
        def foo(bar): return bar
        self.assertEqual(2, foo())

        @dv()
        def foo(bar): return bar
        self.assertEqual(2, foo())

    def test_callback_param_auto_2(self):
        class cbp(FuncDecorator):
            def decorate(self, func, callback):
                def decorated(self, *args, **kwargs):
                    return callback(func(self, *args, **kwargs))
                return decorated

        @cbp(lambda x: x * 2)
        def che(x, y=0): return x + y

        self.assertEqual(4, che(2))
        self.assertEqual(6, che(2, 1))

    def test_callback_param_auto(self):
        class cbp(FuncDecorator):
            def decorate(self, func, callback):
                def decorated(self, *args, **kwargs):
                    return func(self, *args, **kwargs)
                return decorated

        class Bar(object):
            @cbp(lambda *args: (len(args) == 2))
            def che2(self, *args): return 2

            @cbp(lambda *args: (len(args) == 1))
            def che1(self, *args): return 1

        b = Bar()
        self.assertEqual(2, b.che2())
        self.assertEqual(1, b.che1())

    def test_callback_param_explicit(self):
        class cbp(FuncDecorator):
            required_args = True
            def decorate(self, func, callback):
                def decorated(self, *args, **kwargs):
                    return func(self, *args, **kwargs)
                return decorated

        class Bar(object):
            @cbp(lambda *args: (len(args) == 2))
            def che2(self, *args): return 2

            @cbp(lambda *args: (len(args) == 1))
            def che1(self, *args): return 1

        b = Bar()
        self.assertEqual(2, b.che2())
        self.assertEqual(1, b.che1())

    def test_inspect(self):
        class dec1(decorators.FuncDecorator):
            def decorate(self, func, *dec_a, **dec_kw):
                def wrapper(*args, **kwargs):
                    pout.h()
                    return func(*args, **kwargs)
                return wrapper

        class Foo(object):
            @dec1
            def bar(self, *args, **kwargs):
                return 1

            def che(self):
                return 2

        import inspect

        f = Foo()
        methods = inspect.getmembers(f, inspect.isroutine)
        self.assertEqual(2, len([m for m in methods if not m[0].startswith('__')]))

    def test_multi(self):

        class dec1(decorators.FuncDecorator):
            def decorate(self, func, *dec_a, **dec_kw):
                def wrapper(*args, **kwargs):
                    ret = func(*args, **kwargs)
                    ret += 1
                    return ret
                return wrapper

        class dec2(decorators.FuncDecorator):
            def decorate(self, func, *dec_a, **dec_kw):
                def wrapper(*args, **kwargs):
                    ret = func(*args, **kwargs)
                    ret += 1
                    return ret
                return wrapper

        @dec2
        @dec1
        def bar(*args, **kwargs):
            return 1
        # bar = dec2(dec1(bar))
        r = bar()
        self.assertEqual(3, r)

        @dec2
        @dec1(1, 2)
        def foo(*args, **kwargs):
            return 2
        r = foo()
        self.assertEqual(4, r)

        @dec2(1, 2)
        @dec1
        def che(*args, **kwargs):
            return 3
        r = che()
        self.assertEqual(5, r)

        @dec2(1, 2)
        @dec1(3, 4)
        def baz(*args, **kwargs):
            return 4
        r = baz()
        self.assertEqual(6, r)

    def test_well_behaved(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func, *dec_a, **dec_kw):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper

        @dec
        def bar(*args, **kwargs):
            """bar docs"""
            return 1
        self.assertEqual('bar', bar.__name__)
        self.assertEqual('bar docs', bar.__doc__)

        @dec(1, 2)
        def foo(*args, **kwargs):
            """foo docs"""
            return 1
        self.assertEqual('bar', bar.__name__)
        self.assertEqual('bar docs', bar.__doc__)

    def test_no_params_on_function(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper

        @dec
        def bar(*args, **kwargs):
            return 1

        r = bar()
        self.assertEqual(1, r)

    def test_params_init_on_function(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func, *dec_args, **dec_kw):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper

        @dec(1, 2)
        def bar(*args, **kwargs):
            return 1

        @dec()
        def che(*args, **kwargs):
            return 2

        r = bar()
        self.assertEqual(1, r)

        r = che()
        self.assertEqual(2, r)

    def test_no_params_on_classmethod(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func, *dec_a, **dec_kw):
                def wrapper(cls, *args, **kwargs):
                    return func(cls, *args, **kwargs)
                return wrapper

        class Foo(object):
            @classmethod
            @dec
            def bar(cls, test_instance, *args, **kwargs):
                test_instance.assertTrue(issubclass(cls, Foo))
                return 1

        r = Foo.bar(self)
        self.assertEqual(1, r)

    def test_params_on_classmethod(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func, *decorator_args, **dec_kw):
                def wrapper(cls, test_instance, *args, **kwargs):
                    test_instance.assertEqual((1, 2), decorator_args)
                    return func(cls, test_instance, *args, **kwargs)
                return wrapper

        class Foo(object):
            @classmethod
            @dec(1, 2)
            def bar(cls, test_instance, *args, **kwargs):
                test_instance.assertTrue(issubclass(cls, Foo))
                return 1

        r = Foo.bar(self)
        self.assertEqual(1, r)

    def test_init_on_classmethod(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func):
                def wrapper(cls, *args, **kwargs):
                    return func(cls, *args, **kwargs)
                return wrapper

        class Foo(object):
            @classmethod
            @dec()
            def bar(cls, test_instance, *args, **kwargs):
                test_instance.assertTrue(issubclass(cls, Foo))
                return 1

        r = Foo.bar(self)
        self.assertEqual(1, r)

    def test_no_params_on_method(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func):
                def wrapper(self, *args, **kwargs):
                    return func(self, *args, **kwargs)
                return wrapper

        class Foo(object):
            @dec
            def bar(self, test_instance, *args, **kwargs):
                test_instance.assertTrue(isinstance(self, Foo))
                return 1

        f = Foo()
        r = f.bar(self)
        self.assertEqual(1, r)

    def test_params_on_method(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func, *decorator_args, **dec_kw):
                def wrapper(self, test_instance, *args, **kwargs):
                    test_instance.assertEqual((1, 2), decorator_args)
                    return func(self, test_instance, *args, **kwargs)

                return wrapper

        class Foo(object):
            @dec(1, 2)
            def bar(self, test_instance, *args, **kwargs):
                test_instance.assertTrue(isinstance(self, Foo))
                return 1

        f = Foo()
        r = f.bar(self)
        self.assertEqual(1, r)

    def test_init_on_method(self):
        class dec(decorators.FuncDecorator):
            def decorate(self, func):
                def wrapper(self, *args, **kwargs):
                    return func(self, *args, **kwargs)

                return wrapper

        class Foo(object):
            @dec()
            def bar(self, test_instance, *args, **kwargs):
                test_instance.assertTrue(isinstance(self, Foo))
                return 1

        f = Foo()
        r = f.bar(self)
        self.assertEqual(1, r)


