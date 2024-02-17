from random import randrange


def get_random_color():
    r = hex(randrange(0, 255))[2:].zfill(2)
    g = hex(randrange(0, 255))[2:].zfill(2)
    b = hex(randrange(0, 255))[2:].zfill(2)
    return '#'  + r + g + b
