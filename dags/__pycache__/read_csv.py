import pandas as pd



dataframe = pd.read_excel(
    '/Users/malo/airflow-docker/data/organizations-500000.xlsx'
)

print(dataframe)
