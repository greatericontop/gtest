
from random import randint

def gen_small():
    print(5)
    print(randint(1, 25))
    print(' '.join(str(randint(1, 15)) for _ in range(5)))


def gen_medium():
    print(1000)
    print(randint(1, 25000))
    print(' '.join(str(randint(1, 15000)) for _ in range(1000)))
