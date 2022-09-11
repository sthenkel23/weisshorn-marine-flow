def random_fruit():
    return "apple"


def test_random_fruit_slow():
    assert random_fruit() in ["apple", "banana", "orange"]
