# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116


"json"


import unittest


from objx import Object, dumps, loads


VALIDJSON = "{'test': 'bla'}"
VALIDPYTHON = '{"test": "bla"}'
# VALIDPYTHON = '{"test": "bla", "__type__": "opr.objects.Object"}'


class TestDecoder(unittest.TestCase):
    def test_loads(self):
        obj = Object()
        obj.test = "bla"
        oobj = loads(dumps(obj))
        self.assertEqual(oobj.test, "bla")


class TestEncoder(unittest.TestCase):
    def test_dumps(self):
        obj = Object()
        obj.test = "bla"
        self.assertEqual(dumps(obj), VALIDPYTHON)
