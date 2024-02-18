OBX
###

NAME

::

    OBX - objects library


INSTALL

::

    $ pip install obx


SYNOPSIS

::

    >>> from obx import Object, dumps, loads
    >>> o = Object()
    >>> o.a = "b"
    >>> txt = dumps(o)
    >>> loads(txt)
    {"a": "b"}


DESCRIPTION

::

    OBX provides an obx namespace that allows for easy json save//load
    of objects. It provides an "clean namespace" Object class that only
    has dunder methods, so the namespace is not cluttered with method
    names. This makes storing and reading to/from json possible.

    OBX is Public Domain.


AUTHOR

::

    Bart Thate <bthate@dds.nl>


COPYRIGHT

::

    OBX is Public Domain.
