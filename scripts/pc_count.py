import pandas as pd
import numpy as np

icd_person_path = '../raw_data/icd_person_full.csv'
tree_file_path = '../raw_data/icd10_with_parent.csv'
#testing_tree_file_path = '../raw_data/tree_testing_set.csv'

def _trim_icd(icd_string):
	if len(icd_string) > 7 :
		icd_string = icd_string[:-1]
	while icd_string[-1] == '.' or icd_string[-1] == 'X':
		icd_string = icd_string[:-1]
	return icd_string

def clean_icd_person(df_icd, df_tree):
	print('Cleaning ICD_data')
	df_icd['icd'] = df_icd['icd'].apply(_trim_icd)
	all_icd = set(df_tree['icd'].unique())
	missing_icd_records = df_icd[~df_icd['icd'].isin(all_icd)]
	df_icd.drop(missing_icd_records.index, inplace=True)
	breakpoint()
	df_icd.sort_values(by=['icd'], inplace=True)
	df_icd.reset_index(drop=True, inplace=True)
	return missing_icd_records

def _get_own_set(df_icd, df_tree):
	print('generating sets')
	set_list = []
	index_tracker = 0
	icd_series = df_icd['icd']
	person_series = df_icd['person_key']
	appearance = set(df_icd['icd'].unique())
	max_pos = len(df_icd) - 1
	for i, r in df_tree.iterrows():
		icd_code = r['icd']
		#set_list.append(set(df_icd[df_icd.icd == icd_code]['person_key']))
		#Poor performance
		if index_tracker < max_pos and icd_code == df_icd.loc[index_tracker, 'icd']:
			appearance.remove(icd_code)
			start_pos = index_tracker
			end_pos = start_pos
			while end_pos < max_pos and icd_series.loc[end_pos] == icd_code:
				end_pos += 1
			#print(icd_code + ' has '+ str(end_pos - start_pos)+' patients')
			set_list.append(set(person_series.iloc[start_pos:end_pos]))
			index_tracker = end_pos
		else:
			set_list.append(set())
	return set_list 

def _get_desc_index(index, df):
	#return a list of index of it direct descdent
	children = list(df[df.parent == df.loc[index, 'icd']].index.values)
	return children 

def _add_desc_all(df, set_ls, index):
	children = _get_desc_index(index, df)
#	print('processing line ' + str(index) + '...')
	if len(children) > 0:
		for i in children:
			_add_desc_all(df, set_ls, i)
			set_ls[index].update(set_ls[i])

def count_df(df, set_ls):
	pc_ls = []
	for i in set_ls:
		pc_ls.append(len(i))
	df['pc'] = pc_ls

def generate_set_df(df_icd, df_tree):
	person_key_set_list = _get_own_set(df_icd, df_tree)
	root_index = int(df_tree[df_tree['icd'] == 'root'].index.values)
	print('checking duplicated patients')
	_add_desc_all(df_tree, person_key_set_list, root_index)
	count_df(df_tree, person_key_set_list)
	return df_tree

def format_tree(tree):
	to_be_changed_row = tree.icd.str.contains('-')
	tree.loc[to_be_changed_row, 'description'] = tree[to_be_changed_row].description.apply(lambda x: x.split('(')[0].strip())
	return tree

def main():
	icd_person = pd.read_csv(icd_person_path,sep=';')
	tree = pd.read_csv(tree_file_path)
	#drop rows with the same icd and parent
	tree.drop(tree[tree['parent']==tree['icd']].index, inplace=True)
	tree.sort_values(by=['icd'],inplace=True)
	tree.reset_index(drop=True, inplace=True)
	#tree = pd.read_csv(testing_tree_file_path)
	missing_data = clean_icd_person(icd_person, tree)
	final_df = generate_set_df(icd_person, tree)
	final_df = format_tree(final_df)
	final_df.to_csv('../raw_data/final_count.csv',sep=',', index=False)
	print(missing_data)
	missing_data.to_csv('../raw_data/missing_values.csv',sep=';', index=False)

if __name__ == '__main__':
	main()

#Total patients:442589
#Patients in result: 442316
#Covered 99.9% Patients
