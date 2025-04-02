import unittest
from trace_reader import find_data_race

class TestFindDataRace(unittest.TestCase):
    def test_data_race_case_1(self):
        result = find_data_race('races_traces/simple1.txt')
        self.assertEqual(result, (0, 6))

    def test_data_race_case_2(self):
        result = find_data_race('races_traces/simple2.txt')
        self.assertEqual(result, None)

    def test_double_write_1(self):
        result = find_data_race('./races_traces/double_write_race1.txt')
        self.assertEqual(result, (6, 8))

    def test_double_write_2(self):
        result = find_data_race('./races_traces/double_write_race2.txt')
        self.assertEqual(result, (6, 9))

    def test_double_write_no_race1(self):
        result = find_data_race('./races_traces/double_write_no_race1.txt')
        self.assertEqual(result, None)

    def test_double_write_no_race2(self):
        result = find_data_race('./races_traces/double_write_no_race2.txt')
        self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
