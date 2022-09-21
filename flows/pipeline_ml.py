import os
import requests
import pandas as pd

from prefect import flow, task
from google.cloud import firestore


FLOW_NAME = "weisshorn-marine-flow-ml-train"


@task
def retrieve_data(document: str = "prices") -> pd.DataFrame:
    db = firestore.Client.from_service_account_json("./gcl.json")
    d = list(map(lambda x: x.to_dict(), list(db.collection(document).stream())))
    return pd.DataFrame(d)


@task
def transform(df) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df = df.set_index(df.timestamp)

    print(df.dtypes)
    return df

@task
def split(df) -> pd.DataFrame:
    tmin = df.timestamp.min()
    tmax = df.timestamp.max()
    split_num = int(len(df.index)*0.8)
    
    df_train = df[:split_num]
    df_val = df[split_num:len(df.index)]
    
    return df_train, df_val

@flow(name=f"{FLOW_NAME}")
def ml_training_flow():
    df = retrieve_data(document="prices")
    df = transform(df)
    df_train, df_val = split(df)
    
    print(df_train, df_val)
    return df


if __name__ == "__main__":
    ml_training_flow()
