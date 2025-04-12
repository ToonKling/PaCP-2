import unittest
from trace_reader import find_data_race

class TestFindDataRace(unittest.TestCase):

    # Program 1 from overleaf
    def test_data_race_case_1(self):
        result = find_data_race('races_traces/simple1.txt')
        self.assertIn((6, 8), result)

    # Program 1 from overleaf
    def test_data_race_case_2(self):
        result = find_data_race('races_traces/simple2.txt')
        self.assertEqual(result, [])

    # Program 2 from overleaf
    def test_rel_acq_no_race(self):
        result = find_data_race('./races_traces/rel_acq_no_race1.txt')
        self.assertEqual(result, [])

    # Program 3 from overleaf
    def test_program3(self):
        result1 = find_data_race('./races_traces/loops1.txt')
        result2 = find_data_race('./races_traces/loops2.txt')
        self.assertIn((9, 22), result1)
        self.assertIn((10, 7), result2)

    # Program 4 from overleaf
    def test_program4(self):
        result1 = find_data_race('./races_traces/mp.txt')
        self.assertIn((9, 11), result1)

    # Program 5 from overleaf
    def test_program5(self):
        result1 = find_data_race('./races_traces/reorder1.txt')
        result2 = find_data_race('./races_traces/reorder2.txt')
        self.assertIn((9, 22), result1)
        self.assertIn((9, 12), result2)

    # Program 6 from overleaf
    def test_program6(self):
        result1 = find_data_race('./races_traces/seq_cst_no_race1.txt')
        self.assertEqual(result1, [])

    # Program 7 from overleaf
    def test_program7(self):
        result1 = find_data_race('./races_traces/reorder_seq_cst1.txt')
        result2 = find_data_race('./races_traces/reorder_seq_cst2.txt')
        self.assertIn((23, 25), result1)
        self.assertEqual(result2, [])

    # Program 8 is a To do from overleaf
   
    def test_double_write_1(self):
        result = find_data_race('./races_traces/double_write_race1.txt')
        self.assertIn((6, 8), result)

    def test_double_write_2(self):
        result = find_data_race('./races_traces/double_write_race2.txt')
        self.assertIn((9, 10), result)

    def test_double_write_no_race1(self):
        result = find_data_race('./races_traces/double_write_no_race1.txt')
        self.assertEqual(result, [])

    def test_double_write_no_race2(self):
        result = find_data_race('./races_traces/double_write_no_race2.txt')
        self.assertEqual(result, [])


    def test_iriw_1(self):
        result = find_data_race('./races_traces/iriw1.txt')
        self.assertIn((10, 12), result)

    def test_iriw_2(self):
        result = find_data_race('./races_traces/iriw2.txt')
        self.assertIn((10, 11), result)

    def test_iriw_3(self):
        result = find_data_race('./races_traces/iriw3.txt')
        self.assertIn((10, 14), result)

    def test_iriw_4(self):
        result = find_data_race('./races_traces/iriw4.txt')
        self.assertIn((10, 13), result)

    def test_chase_lev_deque(self):
        result = find_data_race('./races_traces/chase_lev_deque1.txt')
        self.assertIn((18, 27), result)

    def test_dekker_fences(self):
        result = find_data_race('./races_traces/dekker_fences1.txt')
        self.assertIn((9, 12), result)

if __name__ == '__main__':
    unittest.main()
