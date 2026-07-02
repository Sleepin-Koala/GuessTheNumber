import random , string


def getName():
    k = random.randint(1, 20)
    return f"player_{''.join([str(i) for i in random.choices(string.digits , k=k)])}"

