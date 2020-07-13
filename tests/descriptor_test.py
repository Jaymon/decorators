# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from collections import Counter

from decorators.compat import *
from decorators import property, classproperty

from . import TestCase, testdata


class ClassPropertyTest(TestCase):
    def test_readonly(self):
        class Foo(object):
            @classproperty
            def bar(cls):
                return 42

        self.assertEqual(42, Foo.bar)

        f = Foo()
        self.assertEqual(42, f.bar)

        Foo.bar = 43
        self.assertEqual(43, f.bar)

        f.bar = 44
        self.assertEqual(44, f.bar)

        with self.assertRaises(TypeError):
            class Foo(object):
                @classproperty
                def bar(cls):
                    return 42

                @bar.setter
                def bar(cls, v):
                    pass

        with self.assertRaises(TypeError):
            class Foo(object):
                @classproperty
                def bar(cls):
                    return 42

                @bar.deleter
                def bar(cls, v):
                    pass

        class Foo(object):
            bar = classproperty(lambda *_: 45, "this is the doc")

        self.assertEqual(45, Foo.bar)


class PropertyTest(TestCase):
    def test_set_init(self):
        counts = Counter()
        def fget(self):
            counts["fget"] += 1
            return self._v

        def fset(self, v):
            counts["fset"] += 1
            self._v = v

        def fdel(self):
            counts["fdel"] += 1
            del self._v

        class FooPropInit(object):
            v = property(fget, fset, fdel, "this is v")
        f = FooPropInit()
        f.v = 6
        self.assertEqual(6, f.v)
        self.assertEqual(2, sum(counts.values()))
        del f.v
        self.assertEqual(3, sum(counts.values()))

        counts = Counter()
        class FooPropInit2(object):
            v = property(fget=fget, fset=fset, fdel=fdel, doc="this is v")
        f = FooPropInit2()
        f.v = 6
        self.assertEqual(6, f.v)
        self.assertEqual(2, sum(counts.values()))
        del f.v
        self.assertEqual(3, sum(counts.values()))

    def test_decorate_init(self):
        counts = Counter()
        class FooPropInit(object):
            @property
            def v(self):
                counts["fget"] += 1
                return self._v

            @v.setter
            def v(self, v):
                counts["fset"] += 1
                self._v = v

            @v.deleter
            def v(self):
                counts["fdel"] += 1
                del self._v

        f = FooPropInit()
        f.v = 6
        self.assertEqual(6, f.v)
        self.assertEqual(2, sum(counts.values()))
        del f.v
        self.assertEqual(3, sum(counts.values()))

    def test_decorate_no_call(self):
        class FooPropInit(object):
            @property
            def v(self):
                return 1

        f = FooPropInit()
        self.assertEqual(1, f.v)

        with self.assertRaises(AttributeError):
            f.v = 6

        with self.assertRaises(AttributeError):
            del f.v

    def test_decorate_call(self):
        class FooPropInit(object):
            @property(cached="_v")
            def v(self):
                return 1

        f = FooPropInit()
        self.assertEqual(1, f.v)

        f.v = 6
        self.assertEqual(6, f.v)

        del f.v
        self.assertEqual(1, f.v)

    def test_cached_no_allow_empty(self):
        counts = Counter()
        class PAE(object):
            @property(cached="_foo", allow_empty=False)
            def foo(self):
                counts["fget"] += 1
                return 0

        c = PAE()
        self.assertEqual(0, c.foo)
        self.assertEqual(0, c.foo)
        self.assertEqual(0, c.foo)
        self.assertEqual(3, counts["fget"])

        c.foo = 1
        self.assertEqual(1, c.foo)
        self.assertEqual(3, counts["fget"])

    def test_cached_setter(self):
        class WPS(object):
            foo_get = False
            foo_set = False
            foo_del = False

            @property(cached="_foo")
            def foo(self):
                self.foo_get = True
                return 1

            @foo.setter
            def foo(self, val):
                self.foo_set = True
                self._foo = val

            @foo.deleter
            def foo(self):
                self.foo_del = True
                del(self._foo)

        c = WPS()

        self.assertEqual(1, c.foo)

        c.foo = 5
        self.assertEqual(5, c.foo)

        del(c.foo)
        self.assertEqual(1, c.foo)

        self.assertTrue(c.foo_get)
        self.assertTrue(c.foo_set)
        self.assertTrue(c.foo_del)

    def test_cached_sharing(self):
        class Foo(object):
            @property(cached="_bar")
            def bar(self):
                return 1

        f = Foo()
        self.assertEqual(1, f.bar)

        f.bar = 2
        self.assertEqual(2, f.bar)

        f2 = Foo()
        self.assertEqual(1, f2.bar)

        f2.bar = 3
        self.assertNotEqual(f.bar, f2.bar)

    def test_strange_behavior(self):
        class BaseFoo(object):
            def __init__(self):
                setattr(self, 'bar', None)

            def __setattr__(self, n, v):
                super(BaseFoo, self).__setattr__(n, v)

        class Foo(BaseFoo):
            @property(cached="_bar", allow_empty=False)
            def bar(self):
                return 1

        f = Foo()
        self.assertEqual(1, f.bar)

        f.bar = 2
        self.assertEqual(2, f.bar)

    def test___dict___direct(self):
        """this is a no win situation

        if you have a bar property and a __setattr__ that modifies directly then
        the other property methods like __set__ will not get called, and you can't
        have property.__get__ look for the original name because there are times
        when you want your property to override a parent's original value for the
        property, so I've chosen to just ignore this case and not support it
        """
        class Foo(object):
            @property(cached="_bar")
            def bar(self):
                return 1
            def __setattr__(self, field_name, field_val):
                self.__dict__[field_name] = field_val
                #super(Foo, self).__setattr__(field_name, field_val)

        f = Foo()
        f.bar = 2 # this will be ignored
        self.assertEqual(1, f.bar)

    def test_lifecycle(self):
        class WP(object):
            counts = Counter()
            @property
            def foo(self):
                self.counts["foo"] += 1
                return 1

            @property()
            def baz(self):
                self.counts["baz"] += 1
                return 2

            @property(cached="_bar")
            def bar(self):
                self.counts["bar"] += 1
                return 3

            @property(cached="_che")
            def che(self):
                self.counts["che"] += 1
                return 4

        c = WP()
        r = c.foo
        self.assertEqual(1, r)
        with self.assertRaises(AttributeError):
            c.foo = 2
        with self.assertRaises(AttributeError):
            del(c.foo)
        c.foo
        c.foo
        self.assertEqual(3, c.counts["foo"])

        r = c.baz
        self.assertEqual(2, r)
        with self.assertRaises(AttributeError):
            c.baz = 3
        with self.assertRaises(AttributeError):
            del(c.baz)

        r = c.bar
        self.assertEqual(3, r)
        self.assertEqual(3, c._bar)
        c.bar = 4
        self.assertEqual(4, c.bar)
        self.assertEqual(4, c._bar)
        del(c.bar)
        r = c.bar
        self.assertEqual(3, r)
        self.assertEqual(2, c.counts["bar"])

        r = c.che
        self.assertEqual(4, r)
        self.assertEqual(4, c._che)
        c.che = 4
        self.assertEqual(4, c.che)
        del(c.che)
        r = c.che
        self.assertEqual(4, r)

    def test_issue_4(self):
        """https://github.com/Jaymon/decorators/issues/4"""
        class Foo(object):
            @property
            def che(self):
                raise AttributeError("This error is caught")

        class Bar(object):
            @property
            def che(self):
                raise AttributeError("This error is lost")
            @property
            def baz(self):
                raise KeyError("_baz")
            def __getattr__(self, k):
                return 1

        b = Bar()
        with self.assertRaises(ValueError):
            b.che
        with self.assertRaises(KeyError):
            b.baz

        f = Foo()
        with self.assertRaises(AttributeError):
            f.che

    def test_setter_kwarg(self):
        class Foo(object):
            @property(setter="_che")
            def che(self, v):
                self._che = v

        f = Foo()
        f.che = 4
        self.assertEqual(4, f.che)

        class Foo(object):
            @property(deleter="_che")
            def che(self):
                del self._che

        f = Foo()
        f.che = 5
        self.assertEqual(5, f.che)

        del f.che

        with self.assertRaises(AttributeError):
            f.che

    def test_readonly(self):
        class Foo(object):
            @property(readonly="_che")
            def che(self):
                print("che getter")
                return 5

        f = Foo()

        with testdata.capture() as o:
            r = f.che
        self.assertEqual(5, r)
        self.assertTrue("che getter" in o)

        with testdata.capture() as o:
            r = f.che
        self.assertEqual(5, r)
        self.assertFalse("che getter" in o)

        with self.assertRaises(AttributeError):
            f.che = 4

        with self.assertRaises(AttributeError):
            del f.che

