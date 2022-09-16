import sys
import requests
from prefect import flow, task
# from prefect.filesystems import GitHub


# block = GitHub(repository="https://github.com/sthenkel23/weisshorn-marine-flow")
# block.get_directory("prefect-block") # specify a subfolder of repo
# block.save("github-storage-dev")


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


@flow(name="weisshorn-marine-flow-20")
def marine_flow(url):
    r = call_api(url)
    price = get_price(r)
    return price


if __name__ == "__main__":
    if sys.argv[1]:
        URL = sys.argv[1]
    else:
        URL = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    while True:
        marine_flow(URL)