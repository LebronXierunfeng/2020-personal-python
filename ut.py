import coverage
import unittest
import GHanalysis

class UT(unittest.TestCase):
    def test_Initialize(self):
        t = GHanalysis.Data("raw_data", 1)

    def test_Query(self):
        t = GHanalysis.Data("raw_data", 1)
        t.getEventsUsers("wade", "PushEvent")
        t.getEventsRepos("james", "PushEvent")
        t.getEventsUsersAndRepos("james", "lakers", "PushEvent")

    # def test_Run(self):
    #     a = GHanalysis.Run()


if __name__ == '__main__':
    unittest.main(verbosity=2)
