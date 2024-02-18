OBJX
####

NAME

::

    OBJX - objects library


INSTALL

::

    $ pip install objx


SYNOPSIS

::

    >>> from objx import Object, dumps, loads
    >>> o = Object()
    >>> o.a = "b"
    >>> txt = dumps(o)
    >>> loads(txt)
    {"a": "b"}


DESCRIPTION

::

    OBJX provides an objx namespace that allows for easy json save//load
    of objects. It provides an "clean namespace" Object class that only
    has dunder methods, so the namespace is not cluttered with method
    names. This makes storing and reading to/from json possible.

    OBJX is Public Domain.


AUTHOR

::

    Bart Thate <objx@proton.me>


COPYRIGHT

::

    OBJX is Public Domain.
