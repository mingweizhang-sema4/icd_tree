import pandas as pd 

FILE_PATH = 'raw_data/final_count_new.csv'

df = pd.read_csv(FILE_PATH)
to_be_changed_row = df.icd.str.contains('-')
df.loc[to_be_changed_row, 'description'] = df[to_be_changed_row].description.apply(lambda x: x.split('(')[0].strip())
df.to_csv('raw_data/final_count.csv',sep=',', index=False)