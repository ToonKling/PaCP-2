import unittest
from trace_reader import find_data_race

class TestFindDataRace(unittest.TestCase):
    def test_data_race_case_1(self):
        dir = 'races_traces/simple1.txt'
        result = find_data_race(dir)
        self.assertEqual(result, (0, 6))

    # def test_data_race_case_2(self):
    #     result = find_data_race(input_data_2)
    #     self.assertEqual(result, expected_output_2)

if __name__ == '__main__':
    unittest.main()