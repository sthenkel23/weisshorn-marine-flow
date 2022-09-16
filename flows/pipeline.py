import sys
import requests
from prefect import flow, task

from marine_flow.data.api import printing

FLOW_NAME = "weisshorn-marine-flow-3022"


@task
def call_api(url):
    response = requests.get(url, timeout=10)
    print(response.status_code)
    return response.json()


@task
def call_api_backend(item="bar"):
    response = requests.get(f"http://weisshorn-backend.herokuapp.com/items/{item}",timeout=10)
    print(response.status_code)
    print(response.json())
    return response.json()


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
    call_api_backend("bar")
    return price


if __name__ == "__main__":
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    else:
        URL = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    marine_flow(URL)
