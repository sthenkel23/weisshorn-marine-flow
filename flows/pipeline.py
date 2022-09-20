import os
import sys
import requests
import pandas as pd
from prefect import flow, task

from marine_flow.data.api import printing

FLOW_NAME = "weisshorn-marine-flow-5000"


@task
def call_api(url):
    response = requests.get(url, timeout=10)
    print(response.status_code)
    return response.json()


@task
def post_api_backend(item) -> pd.DataFrame:
    try:
        r = requests.post(f"{os.environ['HEROKU_API_NAME']}/items/", json=item)
        print(r.status_code)
        print(r.json())
        return pd.DataFrame.from_dict([r.json()])
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


@task
def call_api_backend(item="bar") -> pd.DataFrame:
    try:
        r = requests.get(f"{os.environ['HEROKU_API_NAME']}/items/{item}", timeout=10)
        print(r.status_code)
        print(r.json())
        return pd.DataFrame.from_dict([r.json()])
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


@task
def get_price(response):
    r = response["data"]
    print(r["amount"])
    return r["amount"]


@flow(name=f"{FLOW_NAME}")
def marine_flow(url):
    r = call_api(url)
    price = get_price(r)
    printing()
    item = {"name": "Bar10000", "description": "Epic stuff", "price": 620, "tax": 2.2}
    df = post_api_backend(item)
    print(f"\n\n\n{df.describe}")
    call_api_backend("bar")
    return price


if __name__ == "__main__":
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    else:
        URL = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    marine_flow(URL)
