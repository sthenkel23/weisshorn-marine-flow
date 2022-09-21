import os
import sys
import requests
import pandas as pd
from datetime import datetime
from prefect import flow, task

FLOW_NAME = "weisshorn-marine-flow-ml-train"


@task
def call_api(
    url: str = "https://api.coinbase.com/v2/prices/ETH-USD", price: str = "spot"
) -> pd.DataFrame:
    """_summary_

    :param url: _description_, defaults to "https://api.coinbase.com/v2/prices/ETH-USD"
    :type url: _type_, optional
    :param price: _description_, defaults to "spot"
    :type price: str, optional
    :raises SystemExit: _description_
    :return: _description_
    :rtype: pd.DataFrame
    """
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
    """_summary_

    :param df: _description_
    :type df: _type_
    :raises SystemExit: _description_
    :return: _description_
    :rtype: pd.DataFrame
    """
    d = df.to_dict(orient='records')[0]
    try:
        r = requests.post(f"{os.environ['HEROKU_API_NAME']}/api_prices/", json=d)
        print(r.status_code)
        return pd.DataFrame.from_dict([r.json()])
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


@flow(name=f"{FLOW_NAME}")
def ml_training_flow(url):
    """_summary_

    :param url: _description_
    :type url: _type_
    :return: _description_
    :rtype: _type_
    """
    df = call_api(url)
    df = post_api_backend(df)
    return df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    else:
        URL = "https://api.coinbase.com/v2/prices/ETH-USD"

    ml_training_flow(URL)
