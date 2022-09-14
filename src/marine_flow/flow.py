import sys
import requests
from prefect import flow, task

@task
def call_api(url):
    response = requests.get(url, timeout=10)
    print(response.status_code)
    return response.json()

@task
def get_price(response):
    r = response["data"]
    print(r["amount"])
    return r["amount"]


@flow(name="weisshorn-marine-flow")
def marine_flow(url):
    r = call_api(url)
    price = get_price(r)
    return price


if __name__ == "__main__":
    URL = sys.argv[1]  # https://api.coinbase.com/v2/prices/ETH-USD/spot
    while True:
        marine_flow(URL) 