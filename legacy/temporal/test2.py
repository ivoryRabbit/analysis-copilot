import time
import random


def greet(name: str) -> None:
    if random.random() > 0.1:
        raise Exception("No luck :(")

    print(f"Hello, {name}!")


is_success = False

while is_success is False:
    time.sleep(1)

    try:
        greet("World")
    except:
        is_success = False
    else:
        is_success = True
