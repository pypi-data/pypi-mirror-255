import unittest
from reeco import Validator

class Test(unittest.TestCase):
    """
        The basic class that inherits unittest.TestCase
        """
        validator = Validator()

        # test case function to check the Person.set_name function
        def test_0_set_name(self):
            print("Start set_name test\n")
            """
            Any method which starts with ``test_`` will considered as a test case.
            """
            raise Exception
            return

if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()