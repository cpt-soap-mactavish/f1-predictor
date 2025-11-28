import pandas as pd

df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv')
print('Total columns:', len(df.columns))
print('\nAll columns:')
for i, col in enumerate(df.columns):
    print(f'{i+1}. {col}')

print(f'\nDataset shape: {df.shape}')
print(f'\nFirst few rows:')
print(df.head(2))
