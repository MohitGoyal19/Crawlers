import pandas as pd

pd.read_csv('items_jnbk_2.csv').drop_duplicates().to_excel('jnbk.xlsx', index=None)
