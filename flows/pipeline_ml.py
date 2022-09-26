import os
import requests
import pandas as pd

from prefect import flow, task
from google.cloud import firestore
from marine_flow.models.gp_reg_singletask import fill_response


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
    # @TODO: Implement ts cut
    print(df.dtypes)
    return df


@task
def split(df) -> pd.DataFrame:
    split_num = int(len(df.index)*0.8)
    df_train = df[:split_num]
    df_test = df[split_num:len(df.index)]
    return df_train, df_test

@task
def train(df_train):
    model = "placeholder"
    ckp = "placeholder"
    return model, ckp


@task
def val(model, ckp, df_val):
    metric = "measure - model"
    return metric


@flow(name=f"{FLOW_NAME}")
def ml_training_flow():
    df = retrieve_data(document="prices")
    df = transform(df)
    df_train, df_test = split(df)
    model, ckp = train(df_train)
    metric = val(model, ckp, df_test)

    return df


if __name__ == "__main__":
    ml_training_flow()
