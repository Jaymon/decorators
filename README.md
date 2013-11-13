# Decorators

## The problem

Python has a few forms for decorators, you can have a plain simple decorator, with no arguments:

```python
@mydecorator
def foo(): pass
```

Or a decorator with some arguments:

```python
@mydecorator(1, 2)
def foo(): pass
```

You can even decorate a class:

```python
@mydecorator
class Foo(object): pass
```

and each form is a little different to implement. This was frustrating if you wanted to create easy to use decorators where the developer didn't need to worry about `@mydecorator()` working differently than `@mydecorator`.

## decorators module

The `decorators` module allows you to easily create broad decorators that encompass all forms and all types (functions, methods, classes) using the same interface:

```python
import decorators

class mydecorator(decorators.Decorator):
    def decorate_func(self, func, *dec_args, **dec_kwargs):
        def decorator(*args, *kwargs):
            print "You passed into the decorator these arguments", dec_args, dec_kwargs
            print "You passed into your function these arguments", args, kwargs
            print "Your function is", func
            return func(*args, **kwargs)

        return decorator

    def decorate_class(self, klass, *dec_args, **dec_kwargs):
        print "You passed into the decorator these arguments", dec_args, dec_kwargs
        print "Your class is", klass
        return klass
```

You can then use this decorator:

```python
@mydecorator
def foo(): print "foo()"

@mydecorator(1, 2, boom="blam")
def bar(*args, **kwargs): print "bar()"

@mydecorator
class Baz(object): pass

@mydecorator(1, 2, boom="blam")
class Che(object): pass
```

Now, your decorator can decorate functions or classes, pass in arguments, or not, and you never have to worry about the subtle differences between the decorators, and best of all, you don't have to duplicate code.

## Other decorators

The `Decorator` class is good if you want to create a decorator that is totally flexible, if you want to enforce your decorator only being used for a function/method, you can use `FuncDecorator`. If you want to only decorate a class, use `ClassDecorator`, and if you want to decorate every instance of a class, use `InstanceDecorator`.

```python
import decorators

class only_func(FuncDecorator):
    def decorate(self, func, *dec_a, **dec_kw):
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)
        return decorator

# this will work
@only_func
def foo(): pass

# this will fail
@only_func
class Foo(object): pass
```

## Installation

Use pip:

    pip install decorators

Or, to get the latest and greatest from source:

    pip install ...

## License

MIT

