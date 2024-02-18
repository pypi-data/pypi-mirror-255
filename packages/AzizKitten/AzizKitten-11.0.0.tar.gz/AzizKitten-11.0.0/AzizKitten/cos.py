def cos(x, deg=False):
    from .sin import sin
    from .constants import pi
    if deg:
        x = pi*(x/180)
    return 2**.5 * sin(x + pi/4) - sin(x)