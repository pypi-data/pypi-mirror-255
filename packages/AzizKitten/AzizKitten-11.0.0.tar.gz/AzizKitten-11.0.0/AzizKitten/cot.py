def cot(x, deg=False):
    from .tan import tan
    from .constants import pi
    if deg:
        x = pi*(x/180)
    return 1/tan(x)
