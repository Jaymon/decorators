# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from collections import Counter

from decorators.compat import *
from decorators.misc import (
    once,
    deprecated,
)

from . import TestCase, testdata


class OnceTest(TestCase):
    def test_call(self):

        @once
        def foo(v1, v2):
            print("once")
            return v1 + v2

        with testdata.capture(loggers=False) as c1:
            r1 = foo(1, 2)
        self.assertTrue("once" in c1)

        with testdata.capture(loggers=False) as c1:
            r2 = foo(1, 2)
        self.assertFalse("once" in c1)
        self.assertEqual(r1, r2)

        with testdata.capture(loggers=False) as c2:
            r3 = foo(3, 4)
        self.assertTrue("once" in c2)
        self.assertNotEqual(r3, r2)

        with testdata.capture(loggers=False) as c2:
            r4 = foo(3, 4)
        self.assertFalse("once" in c2)
        self.assertNotEqual(r4, r2)
        self.assertEqual(r3, r4)

    def test_inheritance(self):
        class InFoo(object):
            @property
            @once
            def bar(self):
                print("bar")
                return 10
            @classmethod
            @once
            def bar_method(cls):
                print("bar_method")
                return 12
        class InChe(InFoo): pass
        class InBoo(InChe): pass

        # instance method/property
        f = InFoo()
        with testdata.capture(loggers=False) as c:
            f.bar
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            f.bar
        self.assertFalse("bar" in c)

        che = InChe()
        with testdata.capture(loggers=False) as c:
            che.bar
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            che.bar
        self.assertFalse("bar" in c)

        b = InBoo()
        with testdata.capture(loggers=False) as c:
            b.bar
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            b.bar
        self.assertFalse("bar" in c)

        f = InBoo()
        with testdata.capture(loggers=False) as c:
            f.bar
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            f.bar
        self.assertFalse("bar" in c)

        # standalone function
        @once
        def bar_func(i):
            print("bar")
            return 11
        with testdata.capture(loggers=False) as c:
            bar_func(300)
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            bar_func(300)
        self.assertFalse("bar" in c)

        # classmethod
        with testdata.capture(loggers=False) as c:
            InFoo.bar_method()
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            InFoo.bar_method()
        self.assertFalse("bar" in c)

        with testdata.capture(loggers=False) as c:
            InChe.bar_method()
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            InChe.bar_method()
        self.assertFalse("bar" in c)

        with testdata.capture(loggers=False) as c:
            InBoo.bar_method()
        self.assertTrue("bar" in c)
        with testdata.capture(loggers=False) as c:
            InBoo.bar_method()
        self.assertFalse("bar" in c)


class DeprecatedTest(TestCase):
    def test_deprecated_func(self):
        @deprecated
        def foo(*args, **kwargs):
            return 1

        @deprecated()
        def bar(*args, **kwargs):
            return 2

        @deprecated("2020-07-12")
        def che(*args, **kwargs):
            return 3

        r1 = foo()
        r2 = foo()
        self.assertEqual(r1, r2)

        r1 = bar()
        r2 = bar()
        self.assertEqual(r1, r2)

        r1 = che()
        r2 = che()
        self.assertEqual(r1, r2)

    def test_deprecated_method(self):
        class DC(object):
            @deprecated
            def foo(*args, **kwargs):
                return 1

            @deprecated()
            def bar(*args, **kwargs):
                return 2

            @deprecated("2020-07-12")
            def che(*args, **kwargs):
                return 3

        o = DC()
        r1 = o.foo()
        r2 = o.foo()
        self.assertEqual(r1, r2)

        r1 = o.bar()
        r2 = o.bar()
        self.assertEqual(r1, r2)

        r1 = o.che()
        r2 = o.che()
        self.assertEqual(r1, r2)

    def test_deprecated_class(self):
        @deprecated
        class Foo(object): pass

        @deprecated()
        class Bar(object): pass

        @deprecated("2020-07-12")
        class Che(object): pass

        r1 = Foo()
        r2 = Foo()
        self.assertEqual(type(r1), type(r2))

        r1 = Bar()
        r2 = Bar()
        self.assertEqual(type(r1), type(r2))

        r1 = Che()
        r2 = Che()
        self.assertEqual(type(r1), type(r2))

