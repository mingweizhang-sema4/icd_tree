import count_tree as ct
import pandas as pd
import numpy as np
import unittest

class TestCountTree(unittest.TestCase):
	test_clean = pd.DataFrame([
		['root', 'A', 1],
		['A', 'A1XXD', 2],
		['A', 'A2XD', 3],
		['root', 'B', 4],
		['B', 'B1', 5],
		['B', 'B1', 7],
		['B1', 'B12.3458', 10]
	], columns = ['parent', 'icd', 'pc'])
	test_clean_copy = test_clean	
	# test_tree = ct.tree_df[:100]
	# test_pc = ct.pc_df[:100]
	
	def test_trim_icd(self):
		self.assertEqual(ct._trim_icd('A10'), 'A10')
		self.assertEqual(ct._trim_icd('A10.325'), 'A10.325')
		self.assertEqual(ct._trim_icd('A10.3257'), 'A10.325')
		self.assertEqual(ct._trim_icd('A10.3X'), 'A10.3')
		self.assertEqual(ct._trim_icd('A10.3XXD'), 'A10.3')
		self.assertEqual(ct._trim_icd('A10.325D'), 'A10.325')
		self.assertEqual(ct._trim_icd(''), '')
		self.assertEqual(ct._trim_icd('X80.XXXD'), 'X80')


	def test_remove_ext(self):
		ct._remove_ext(test_clean)
		self.assertEqual(test_clean['icd'], pd.Series(['A', 'A1', 'A2', 'B', 'B1', 'B1', 'B12.345']))

	def test_add_dups(self):
		ct._add_dups(test_clean)
		self.assertEqual(test_clean['pc'], pd.Series([1, 2, 3, 4, 12, 10]))
		# self.assertEqual(test_clean.shape[0, 6])

	def test_clean_pc(self):
		test_clean = test_clean_copy
		ct.clean_pc(test_clean)
		self.assertEqual(test_clean.shape, (3, 6))

	def test_find_children(self):
		pass	

if __name__ == '__main__':
	unittest.main()
