import os
import sys
import requests
import pandas as pd
from datetime import datetime
from prefect import flow, task

FLOW_NAME = "weisshorn-marine-flow-get-prices-time"


@task
def call_api(
    url: str = "https://api.coinbase.com/v2/prices/ETH-USD", price: str = "spot"
) -> pd.DataFrame:
    try:
        r = requests.get(f"{url}/{price}", timeout=10)
        print(r.status_code)
        r = r.json()["data"]
        r["timestamp"] = str(datetime.utcnow())
        return pd.DataFrame.from_dict([r])
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


@task
def post_api_backend(df) -> pd.DataFrame:
    d = df.to_dict(orient='records')[0]
    try:
        r = requests.post(f"{os.environ['HEROKU_API_NAME']}/api_prices/", json=d)
        print(r.status_code)
        return pd.DataFrame.from_dict([r.json()])
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


@flow(name=f"{FLOW_NAME}")
def marine_flow(url):
    df = call_api(url)
    df = post_api_backend(df)
    return df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    else:
        URL = "https://api.coinbase.com/v2/prices/ETH-USD"

    marine_flow(URL)
