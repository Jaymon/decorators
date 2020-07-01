# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from collections import Counter

from decorators.compat import *
from decorators import property

from . import TestCase, testdata


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

        f.v = 6
        self.assertEqual(6, f.v)

        del f.v
        self.assertEqual(1, f.v)

    def test_decorate_call(self):
        class FooPropInit(object):
            @property()
            def v(self):
                return 1

        f = FooPropInit()
        self.assertEqual(1, f.v)

        f.v = 6
        self.assertEqual(6, f.v)

        del f.v
        self.assertEqual(1, f.v)

    def test_no_allow_empty(self):
        counts = Counter()
        class PAE(object):
            @property(allow_empty=False)
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

    def test_setter(self):
        class WPS(object):
            foo_get = False
            foo_set = False
            foo_del = False

            @property(cached=True)
            def foo(self):
                self.foo_get = True
                return 1

            @foo.setter
            def foo(self, val):
                self.foo_set = True
                #pout.v(type(self).foo)
                type(self).foo.value = val
                #self._foo = val

            @foo.deleter
            def foo(self):
                self.foo_del = True
                #del(self._foo)
                del type(self).foo.value

        c = WPS()

        self.assertEqual(1, c.foo)

        c.foo = 5
        self.assertEqual(5, c.foo)

        del(c.foo)
        self.assertEqual(1, c.foo)

        self.assertTrue(c.foo_get)
        self.assertTrue(c.foo_set)
        self.assertTrue(c.foo_del)

    def test_sharing(self):
        class Foo(object):
            @property(cached=True)
            def bar(self):
                return 1

        f = Foo()
        self.assertEqual(1, f.bar)

        f.bar = 2
        self.assertEqual(2, f.bar)

        f2 = Foo()
        self.assertEqual(1, f.bar)






class XPropertyTest(TestCase):
    def test__property__strange_behavior(self):
        class BaseFoo(object):
            def __init__(self):
                setattr(self, 'bar', None)

            def __setattr__(self, n, v):
                super(BaseFoo, self).__setattr__(n, v)

        class Foo(BaseFoo):
            @endpoints.decorators._property(allow_empty=False)
            def bar(self):
                return 1

        f = Foo()
        self.assertEqual(1, f.bar)

        f.bar = 2
        self.assertEqual(2, f.bar)

    def test__property___dict__direct(self):
        """
        this is a no win situation
        if you have a bar _property and a __setattr__ that modifies directly then
        the other _property values like __set__ will not get called, and you can't
        have _property.__get__ look for the original name because there are times
        when you want your _property to override a parent's original value for the
        property, so I've chosen to just ignore this case and not support it
        """
        class Foo(object):
            @endpoints.decorators._property
            def bar(self):
                return 1
            def __setattr__(self, field_name, field_val):
                self.__dict__[field_name] = field_val
                #super(Foo, self).__setattr__(field_name, field_val)

        f = Foo()
        f.bar = 2 # this will be ignored
        self.assertEqual(1, f.bar)

    def test__property(self):
        class WP(object):
            count_foo = 0

            @endpoints.decorators._property(True)
            def foo(self):
                self.count_foo += 1
                return 1

            @endpoints.decorators._property(read_only=True)
            def baz(self):
                return 2

            @endpoints.decorators._property()
            def bar(self):
                return 3

            @endpoints.decorators._property
            def che(self):
                return 4

        c = WP()
        r = c.foo
        self.assertEqual(1, r)
        self.assertEqual(1, c._foo)
        with self.assertRaises(AttributeError):
            c.foo = 2
        with self.assertRaises(AttributeError):
            del(c.foo)
        c.foo
        c.foo
        self.assertEqual(1, c.count_foo)

        r = c.baz
        self.assertEqual(2, r)
        self.assertEqual(2, c._baz)
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

        r = c.che
        self.assertEqual(4, r)
        self.assertEqual(4, c._che)
        c.che = 4
        self.assertEqual(4, c.che)
        del(c.che)
        r = c.che
        self.assertEqual(4, r)



