def asin(x):
    from .integrate import integrate
    from .constants import pi
    if -1 <= x <= 1:
        if x == 1:
            return pi/2
        elif x == -1:
            return -(pi/2)
        else:
            def integrand(t):
                return 1/(1-t**2)**.5
            return integrate(integrand, 0, x)
    else:
        raise ValueError("Value input must be in [-1 .. 1]")
