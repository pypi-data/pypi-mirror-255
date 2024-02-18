def csc(x, deg=False):
    from .sin import sin
    from .constants import pi
    if deg:
        x = pi*(x/180)
    return 1/sin(x)
