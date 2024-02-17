import pandas as pd
df = pd.read_csv('../f5c_result_rna/dna/current_feature.csv')
df_group = df.groupby('Position')
for key,temp_df in df_group:
    sample= temp_df[temp_df['Group']=='Sample']['Mean'].median()
    control = temp_df[temp_df['Group'] == 'Control']['Mean'].median()
    print(key,sample-control)
print(1)