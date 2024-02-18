# This file is placed in the Public Domain.
#
# pylint: disable=C,R


"interface"


import logging
import sys
import unittest


import objx


METHODS = [
    "Object",
    "construct",
    "dump",
    "dumps",
    "edit",
    "fmt",
    "fqn",
    "items",
    "keys",
    "load",
    "loads",
    "update",
    "values",
]

METHOS = [
    "JSONDecoder",
    "JSONEncoder",
    "Object",
    "ObjectDecoder",
    "ObjectEncoder",
    "__builtins__",
    "__cached__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__spec__",
    "construct",
    "dump",
    "dumps",
    "hook",
    "json",
    "load",
    "loads",
]


class A(objx.Object):
    def a(self):
        return "b"


DICT = {}


DIFF = [
    "__default__",
    "__dict__",
    "__fnm__",
    "__getattr__",
    "__module__",
    "__slots__",
    "__test__",
    "_pytestfixturefunction",
]
DIFF = ["__dict__", "__module__", "__weakref__"]

DIFF = [
    "__dict__",
    "__module__",
    "__slots__",
]


OBJECT = objx


class TestInterface(unittest.TestCase):
    def test_methodinterface(self):
        okd = True
        for meth in METHODS:
            func1 = getattr(OBJECT, meth)
            if not func1:
                continue
            func2 = DICT.get(meth)
            if not func2:
                continue
            if dir(func1) != dir(func2):
                print(func1, func2)
                okd = False
            sys.stdout.flush()
        self.assertTrue(okd)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("SomeTest.testSomething").setLevel(logging.DEBUG)
    unittest.main()
