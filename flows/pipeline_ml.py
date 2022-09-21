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


@flow(name=f"{FLOW_NAME}")
def ml_training_flow():
    df = retrieve_data(document="prices")
    df = transform(df)
    print(df)
    return df


if __name__ == "__main__":
    ml_training_flow()
