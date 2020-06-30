import pandas as pd

pd.read_csv('items_jnbk_2.csv', low_memory=False).drop_duplicates().to_excel('jnbk.xlsx', index=None)
