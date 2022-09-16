import sys
import requests
from prefect import Flow, task
from prefect.storage import GitHub
from prefect.run_configs import LocalRun


FLOW_NAME = "weisshorn-marine-flow-20"
STORAGE = GitHub(
    repo="sthenkel23/weisshorn-marine-flow",
    path=f"flows/flow.py",
    access_token_secret="GITHUB_ACCESS_TOKEN",  # required with private repositories
)


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


# @flow(name="weisshorn-marine-flow-20")
# def marine_flow(url):
with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=LocalRun(
        labels=["dev"],
    ),
) as marine_flow:
    r = call_api(url)
    price = get_price(r)
    # return price


if __name__ == "__main__":
    URL = sys.argv[1]  # https://api.coinbase.com/v2/prices/ETH-USD/spot
    while True:
        marine_flow(URL)
