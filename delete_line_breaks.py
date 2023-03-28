import pandas as pd

df = pd.read_excel('Remove_breaks.xlsx')

df = df.replace(r'\n', ' ', regex=True)

df.to_excel("No Breaks.xlsx")