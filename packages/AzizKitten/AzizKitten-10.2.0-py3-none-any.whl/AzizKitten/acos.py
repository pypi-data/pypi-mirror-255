def acos(x):
    from .asin import asin
    from .constants import pi
    if -1 <= x <= 1:
        return pi/2 - asin(x)
    else:
        raise ValueError("Value input must be in [-1 .. 1]")
