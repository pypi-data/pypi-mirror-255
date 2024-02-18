def tan(x, deg=False):
    from .sin import sin
    from .cos import cos
    from .constants import pi
    if deg:
        x = pi(x/180)
    return sin(x)/cos(x)
