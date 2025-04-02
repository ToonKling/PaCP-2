import unittest
from trace_reader import find_data_race

class TestFindDataRace(unittest.TestCase):
    def test_data_race_case_1(self):
        result = find_data_race('races_traces/simple1.txt')
        self.assertEqual(result, (6, 8))

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

    # Program 2 from overleaf
    def test_rel_acq_no_race(self):
        result = find_data_race('./races_traces/rel_acq_no_race1.txt')
        self.assertEqual(result, None)

    def test_iriw_1(self):
        result = find_data_race('./races_traces/iriw1.txt')
        self.assertEqual(result, (10, 12))

    def test_iriw_2(self):
        result = find_data_race('./races_traces/iriw2.txt')
        self.assertEqual(result, (10, 11))

    def test_iriw_3(self):
        result = find_data_race('./races_traces/iriw3.txt')
        self.assertEqual(result, (10, 14))

    def test_iriw_4(self):
        result = find_data_race('./races_traces/iriw4.txt')
        self.assertEqual(result, (10, 13))

if __name__ == '__main__':
    unittest.main()
