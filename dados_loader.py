import pandas as pd

def carregar_dados_covid():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    df["date"] = pd.to_datetime(df["date"])
    return df
