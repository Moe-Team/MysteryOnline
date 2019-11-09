import unittest
from MysteryOnline.utils import binary_search


def search(track_list, target):
    found_index = binary_search(track_list, target)
    if found_index is None:
        return None
    i = found_index
    current_track = track_list[i].lower()
    result = []
    while current_track.startswith(target.lower()):
        result.append(current_track)
        if i == len(track_list) - 1:
            break
        i += 1
        current_track = track_list[i].lower()
    i = found_index
    if i > 0:
        i -= 1
        current_track = track_list[i].lower()
        while current_track.startswith(target.lower()):
            result.append(current_track)
            if i == 0:
                break
            i -= 1
            current_track = track_list[i].lower()
    return result


class SearchTest(unittest.TestCase):

    def setUp(self):
        self.test_track_list = ["TestTrack", "Another track", "Yet Another Track", "A2384", "Same", "SameStart",
                                "Same starter", "same start"]
        self.test_track_list.sort(key=str.lower)

    def test_simple_search(self):
        result = search(self.test_track_list, "Yet Another Track")
        self.assertEqual(1, len(result))
        self.assertEqual("yet another track", result[0])

    def test_multiple_results(self):
        result = search(self.test_track_list, "same")
        self.assertEqual(4, len(result))

    def test_first_item_search(self):
        result = search(self.test_track_list, "A2384")
        self.assertEqual(1, len(result))
        self.assertEqual("a2384", result[0])

    def test_not_found(self):
        result = search(self.test_track_list, "Not found")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
