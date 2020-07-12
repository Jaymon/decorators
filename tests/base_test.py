# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from decorators import (
    FuncDecorator,
    ClassDecorator,
    InstanceDecorator,
    Decorator,
)

from . import TestCase, testdata


class DecoratorTest(TestCase):
    def test_classmethod_decorate_func(self):
        class dm(Decorator):
            def decorate_func(self, func, *dc_args, **dc_kwargs):
                return func

        class Foo(object):
            @classmethod
            @dm
            def bar(cls):
                return 5

        r1 = Foo.bar()
        r2 = Foo.bar()
        self.assertEqual(r1, r2)

    def test_classmethod_all(self):
        self.skip_test("""as far as I can tell there is not a good way to infer this
            particular test because it seems to me decorating a class with a function
            might not be that uncommon and @dm(function) on the class is equivalent
            to @dm on the function, and they will both pass the ambiguity check"""
        )
        class dm(Decorator):
            def decorate_func(self, func, *dc_args, **dc_kwargs):
                print("func")
                return func

            def decorate_class(self, cls, *dc_args, **dc_kwargs):
                print("cls")
                return cls

        class Foo(object):
            @classmethod
            @dm
            def bar(cls):
                return 5

        # here is the problem, these calls will actually wrap the class, not the
        # method, as far as I can tell there is no way to discern the difference
        # and I think this is rare enough to not be worth trying to figure out
        # anymore
        r1 = Foo.bar()
        r2 = Foo.bar()
        self.assertEqual(r1, r2)
        self.assertEqual(5, r1)
        self.assertEqual(5, r2)


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
        class dec(ClassDecorator):
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
    def test_classmethod(self):
        class dm(FuncDecorator):
            def decorate(self, func, *dc_args, **dc_kwargs):
                def decorated(*args, **kwargs):
                    return func(*args, **kwargs)
                return decorated

        class Foo(object):
            @classmethod
            @dm
            def bar(cls):
                return 5

        r1 = Foo.bar()
        r2 = Foo.bar()
        self.assertEqual(r1, r2)

    def test_consistency(self):
        """I never tested the new code with multiple calls, turns out they didn't
        work because after it figured out the correct path it sometimes didn't invoke
        the function like it should on the subsequent calls"""
        class dc(FuncDecorator):
            def decorate(self, func, *dc_args, **dc_kwargs):
                def decorated(*args, **kwargs):
                    return func(*args, **kwargs)
                return decorated

        @dc
        def foo(v1, v2):
            return v1 + v2
        r1 = foo(1, 2)
        r2 = foo(1, 2)
        r3 = foo(1, 2)
        self.assertEqual(r1, r2)
        self.assertEqual(r1, r3)

        @dc()
        def bar(v1, v2):
            return v1 + v2
        r1 = bar(1, 2)
        r2 = bar(1, 2)
        r3 = bar(1, 2)
        self.assertEqual(r1, r2)
        self.assertEqual(r1, r3)

        @dc("one")
        def che(v1, v2):
            return v1 + v2
        r1 = che(1, 2)
        r2 = che(1, 2)
        r3 = che(1, 2)
        self.assertEqual(r1, r2)
        self.assertEqual(r1, r3)

        @dc("one", "two")
        def baz(v1, v2):
            return v1 + v2
        r1 = baz(1, 2)
        r2 = baz(1, 2)
        r3 = baz(1, 2)
        self.assertEqual(r1, r2)
        self.assertEqual(r1, r3)

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
        class dec1(FuncDecorator):
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

        class dec1(FuncDecorator):
            def decorate(self, func, *dec_a, **dec_kw):
                def wrapper(*args, **kwargs):
                    ret = func(*args, **kwargs)
                    ret += 1
                    return ret
                return wrapper

        class dec2(FuncDecorator):
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
        class dec(FuncDecorator):
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
        self.assertEqual('foo', foo.__name__)
        self.assertEqual('foo docs', foo.__doc__)

    def test_no_params_on_function(self):
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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
        class dec(FuncDecorator):
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

    def test_func_with_class(self):
        class dec(FuncDecorator):
            def decorate(self, func, *dec_args, **dec_kwargs):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs) + 1
                return wrapper

        class Foo(object): pass

        @dec(Foo)
        def func(): return 3

        r = func()
        self.assertEqual(4, r)


    def test_ambiguity_1(self):
        class dec(FuncDecorator):
            def decorate(self, func, callback=None):
                def wrapper(self, *args, **kwargs):
                    return func(self, *args, **kwargs)
                return wrapper


        @dec(lambda *_, **__: 1)
        def func(callback): return callback()
        r = func(lambda: 2)
        self.assertEqual(2, r)

        @dec()
        def func(callback): return callback()
        r = func(lambda: 3)
        self.assertEqual(3, r)


    def test_ambiguity_2(self):
        self.skip_test("This was used to rewrite because it has every type of decorator")
        import inspect

#         class dec(Dec):
#             def decorate_func(self, f, *args, **kwargs):
#                 return f
# 
#             def decorate_class(self, c, *args, **kwargs):
#                 pout.v(c, args, kwargs)
#                 return c



        class dec(Decorator):
#             def __init__(self, *args, **kwargs):
#                 frames = inspect.stack()
#                 #args, _, _, value_dict = inspect.getargvalues(frames[0][0])
#                 #pout.v(args, value_dict)
#                 pout.v(frames[1])
#                 #pout.i(frames[1][0].f_code)

            def decorate_func(self, f, *args, **kwargs):
                return f

            def decorate_class(self, c, *args, **kwargs):
                #pout.v(c, args, kwargs)
                return c


#         class dec(Basedec):
#             def __init__(self, *args, **kwargs):
#                 super(dec, self).__init__(*args, **kwargs)



#         @dec
#         class Foo(object):
#             pass
#         f = Foo()
#         return





        pout.b("special cases")

        @dec(
        )
        def func(): pass
        func()

        @dec(
            "arg1",
            "arg2",
        )
        def func(): pass
        func()

        pout.b("functions")

        @dec
        def func(): pass
        func()

        @dec()
        def func(): pass
        func()

        @dec("arg1")
        def func(): pass
        func()


        pout.b("methods")

        class Foo(object):
            @dec
            def func(self): pass
        f = Foo()
        f.func()

        class Foo(object):
            @dec()
            def func(self): pass
        f = Foo()
        f.func()

        class Foo(object):
            @dec("arg1")
            def func(self): pass
        f = Foo()
        f.func()

        pout.b("classes")

        @dec
        class Foo(object):
            pass
        f = Foo()


        @dec()
        class Foo(object):
            pass
        f = Foo()

        @dec("arg1")
        class Foo(object):
            pass
        f = Foo()

