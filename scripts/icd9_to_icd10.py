import pandas as pd

DATA_PATH = 'raw_data/all_dx.csv'
MAPPING_TABLE_PATH = 'raw_data/icd9_mapping_icd10.csv'

df = pd.read_csv(DATA_PATH, sep=';',dtype=str)
icd10_df = df[df.code_system == 'ICD-10'].copy()
icdchaos_df = df[df.code_system =='ICD-9'].dropna()
index_filter = icdchaos_df.icd_code.str.contains('^[0-9EV]')
icd9_df = icdchaos_df[index_filter]
icd10_other = icdchaos_df[-index_filter].copy()
mp_df = pd.read_csv(MAPPING_TABLE_PATH, sep=';', dtype=str)
icd9_mapped = icd9_df.merge(mp_df,left_on='icd_code',right_on='icd9',how='left').dropna()
icd9_mapped.drop(['icd_code', 'code_system','icd9','term'], axis=1,inplace=True)
icd9_mapped.reset_index(drop=True,inplace=True)
icd9_mapped.rename(columns={'icd10':'icd'},inplace=True)
icd10_other.drop(['code_system'], axis=1,inplace=True)
icd10_other.reset_index(drop=True, inplace=True)
icd10_other.rename(columns={'icd_code':'icd'},inplace=True)
icd10_df.drop(['code_system'],axis=1,inplace=True)
icd10_df.reset_index(drop=True,inplace=True)
icd10_df.rename(columns={'icd_code':'icd'},inplace=True)
final_df = pd.concat([icd9_mapped, icd10_other, icd10_df],ignore_index=True).drop_duplicates(ignore_index=True)
