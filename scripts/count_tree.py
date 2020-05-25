import pandas as pd
import numpy as np

tree_file_path = '../raw_data/icd10_with_parent.csv'
pc_file_path = '../raw_data/icd_counts_202004061920.csv'

def clean_pc(df):
	df = _remove_ext(df)
	df = _add_dups(df)
	return df

def _remove_ext(df):
	df['icd'] = df['icd'].apply(_trim_icd)
	df = df.drop(columns = ['description'])
	return df

def _trim_icd(string):
	split_list = string.split('X')
	result = split_list[0] if split_list[0] != '' else split_list[1]
	if len(result) > 7:
		result = result[:7]
	if result[-1] == '.':
		result = result[:-1]
	return result

def _add_dups(df):
	df = df.groupby(['icd']).sum()
	return df

def _children_total(icd):
	#TODO
	pass

def _find_children(icd):
	#TODO
	pass

def get_total(icd):
	#TODO
	pass

def main():
	tree_df = pd.read_csv(tree_file_path)
	pc_df = pd.read_csv(pc_file_path, sep = ';')
	pc_df = clean_pc(pc_df)
	combined_df = tree_df.merge(pc_df, how='left', on='icd')
	


if __name__ == '__main__':
	main()

