def sec(x, deg=False):
    from .cos import cos
    from .constants import pi
    if deg:
        x = pi*(x/180)
    return 1/cos(x)
