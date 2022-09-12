from prefect import flow, task


@task
def say_hello():
    print("Hello, World! I'm Marvin!")


@flow(name="marine-flow")
def marine_flow():
    say_hello()


if __name__ == "__main__":
    marine_flow()  # "Hello, World! I'm Marvin!"
