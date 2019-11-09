import unittest
from MysteryOnline.location import Location, SubLocation


class MockUser:

    def __init__(self, name):
        self.name = name


class LocationTests(unittest.TestCase):

    def setUp(self):
        self.location = Location("Hakuryou", directory="../src/locations")

    def test_create_location(self):
        self.assertEqual("Hakuryou", self.location.get_name())
        self.assertEqual("../src/locations/Hakuryou/", self.location.path)

    def test_load_location(self):
        self.location.load()
        self.assertNotEqual({}, self.location.sublocations)

    def test_get_sublocation(self):
        self.location.load()
        self.assertIsInstance(self.location.get_sub("boat"), SubLocation)


class SubLocationTests(unittest.TestCase):

    def setUp(self):
        self.sublocation = SubLocation("Fake", "fake_path")

    def test_adding_users(self):
        test_c_user = MockUser("Test")
        self.sublocation.add_c_user(test_c_user)
        self.assertIs(test_c_user, self.sublocation.get_c_user())
        test_l_user = MockUser("Test")
        self.sublocation.add_l_user(test_l_user)
        self.assertIs(test_l_user, self.sublocation.get_l_user())
        test_r_user = MockUser("Test")
        self.sublocation.add_r_user(test_r_user)
        self.assertIs(test_r_user, self.sublocation.get_r_user())

    def test_return_most_recent_user(self):
        old_user = MockUser("Test")
        recent_user = MockUser("Test")
        self.sublocation.add_r_user(old_user)
        self.sublocation.add_r_user(recent_user)
        self.assertIsNot(old_user, self.sublocation.get_r_user())
        self.assertIs(recent_user, self.sublocation.get_r_user())

    def test_removing_users(self):
        user = MockUser("Test")
        self.sublocation.add_r_user(user)
        self.assertIs(user, self.sublocation.get_r_user())
        self.sublocation.remove_r_user(user)
        self.assertEqual([], self.sublocation.r_users)


if __name__ == '__main__':
    unittest.main()
