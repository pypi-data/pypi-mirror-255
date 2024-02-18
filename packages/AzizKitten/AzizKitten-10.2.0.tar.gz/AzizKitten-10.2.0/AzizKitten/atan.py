def atan(x):
    from .integrate import integrate
    def integrand(t):
        return 1/(1+t**2)
    return integrate(integrand, 0, x)
