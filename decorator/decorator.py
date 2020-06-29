'''
This module provides some decorators to decorate other decorators, 
in order to reduce some boilerplate code.
'''

from functools import partial, reduce, update_wrapper
from typing import Callable, Optional, Union


__all__ = ['decorated', 'pipe', 'compose', 'optional', 'optional2']


__undefined = object()


def decorated(
    f: Callable[[Callable], Callable],
    g: Optional[Callable] = None, 
    /, 
) -> Callable[[Callable], Callable]:
    '''
    This helper function is used to reduce the boilerplate code 
        when creating a decorator.

    :param f: decorator which is decorated by `decorated`.
    :param g: callable which is decorated by `f`.
    :return: a decorated callable, `f` is the decorator and
        g is the callable.

    #>>> Before using this function <<<#
        def foo(bar: Callable, /):
            @functools.wraps(bar)
            def baz(*args, **kwargs):
                return bar(*args, **kwargs)
            return foo

    #>>> After using this function <<<#
        @decorated
        def foo(bar: Callable, /, *args, **kwargs):
            return bar(*args, **kwargs)
    '''
    if g is None:
        return update_wrapper(partial(decorated, f), f)
    return update_wrapper(partial(f, g), g)


def pipe(*decorators: Callable) -> Callable:
    '''
    This helper function is used to combine multiple 
        decorators `decorators` merge into a single whole, 
        and apply from left to right to the decorated object.

    '''
    return decorated(lambda fn, /, *args, **kwargs: 
        reduce(lambda f, g, /: g(f), decorators, fn(*args, **kwargs))
    )


def compose(*decorators: Callable) -> Callable:
    '''
    This helper function is used to combine multiple 
        decorators `decorators` merge into a single whole, 
        and apply from right to left to the decorated object.
    !!! It's just the opposite of `pipe` !!!
    '''
    return pipe(*decorators[::-1])


@decorated
def optional(
    f: Callable[..., Callable],
    g=__undefined,
    /, **kwargs
) -> Callable:
    '''
    This helper function decorates another decorator that having 
        optional parameters. Make sure that these optional parameters 
        are keyword parameters with default values.

    Supposing there is such a decorator:
        >>> @optional
        ... def foo(bar='bar', baz='baz'):
        ...     @decorated
        ...     def wrapped(fn, /, *args, **kwargs):
        ...         print(bar)
        ...         r = fn(*args, **kwargs)
        ...         print(baz)
        ...         return r
        ...     return wrapped
        ... 

    Use case example 1:
        >>> @foo 
        ... def baba1(): 
        ...     print('baba1') 
        ... 
        >>> baba1()
        bar
        baba1
        baz

    Use case example 2:
        >>> @foo()
        ... def baba2(): 
        ...     print('baba2') 
        ... 
        >>> baba2()
        bar
        baba2
        baz

    Use case example 3:
        >>> @foo(bar='bar: begin', baz='baz: end') 
        ... def baba3(): 
        ...     print('baba3: process')
        ... 
        >>> baba3()
        bar: begin
        baba3: process
        baz: end
    '''
    return f(**kwargs) if g is __undefined else f(**kwargs)(g)


@decorated
def optional2(
    f: Callable[..., Callable],
    g=__undefined,
    /, *args, **kwargs
) -> Callable:
    '''
    This helper function decorates another decorator that having 
        optional parameters. Make sure that these optional parameters 
        have default values.

    Supposing there is such a decorator:
        >>> @optional2
        ... def foo(bar, baz='baz'):
        ...     @decorated
        ...     def wrapped(fn, /, *args, **kwargs):
        ...         print(bar)
        ...         r = fn(*args, **kwargs)
        ...         print(baz)
        ...         return r
        ...     return wrapped
        ... 

    Use case example 1:
        >>> @foo
        ... def baba1():
        ...     print('baba1')
        ... 
        Traceback (most recent call last):
            ...
        TypeError: foo() missing 1 required positional argument: 'bar'

    Use case example 2:
        >>> @foo('bar')
        ... def baba2():
        ...     print('baba2')
        ... 
        >>> baba2()
        bar
        baba2
        baz

    Use case example 3:
        >>> @foo(bar='bar')
        ... def baba3():
        ...     print('baba3')
        ... 
        >>> baba3()
        bar
        baba3
        baz

    Supposing there is such a decorator:
        >>> @optional2
        ... def foo2(bar='bar', *, baz='baz'):
        ...     @decorated
        ...     def wrapped(fn, /, *args, **kwargs):
        ...         print(bar)
        ...         r = fn(*args, **kwargs)
        ...         print(baz)
        ...         return r
        ...     return wrapped
        ... 

    Use case example 4:
        >>> @foo2 
        ... def baba4(): 
        ...     print('baba4') 
        ... 
        >>> baba4()
        bar
        baba4
        baz

    Use case example 5:
        >>> @foo2()
        ... def baba5(): 
        ...     print('baba5') 
        ... 
        >>> baba5()
        bar
        baba5
        baz

    Use case example 6:
        >>> @foo2('bar: begin', baz='baz: end') 
        ... def baba6(): 
        ...     print('baba6: process')
        ... 
        >>> baba6()
        bar: begin
        baba6: process
        baz: end
    '''
    if g is __undefined:
        return f(*args, **kwargs)
    elif callable(g):
        return f(*args, **kwargs)(g)
    else:
        return f(g, *args, **kwargs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

