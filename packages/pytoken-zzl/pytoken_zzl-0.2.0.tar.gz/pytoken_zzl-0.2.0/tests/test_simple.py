# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from pytoken_zzl.token import Token


class TestSimple(unittest.TestCase):

    def test_token(self):
        msg = "test"
        token = Token(msg)
        self.assertEqual(token.msg, msg)
        print(token.to_str())
        


if __name__ == '__main__':
    unittest.main()
