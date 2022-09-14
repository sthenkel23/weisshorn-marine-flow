import sys
import requests
from prefect import flow, task

@task
def call_api(url):
    response = requests.get(url, timeout=10)
    print(response.status_code)
    return response.json()

@task
def parse_fact(response):
    fact = response["fact"]
    print(fact)
    return fact


@flow(name="weisshorn-marine-flow")
def marine_flow(url):
    fact_json = call_api(url)
    fact_text = parse_fact(fact_json)
    return fact_text


if __name__ == "__main__":
    URL = sys.argv[1]
    while True:
        marine_flow(URL)  # "Hello, World! I'm Marvin!"
