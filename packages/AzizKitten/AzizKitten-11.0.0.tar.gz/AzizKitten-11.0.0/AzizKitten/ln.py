def ln(x):
    from .integrate import integrate
    def integrand(t):
        return 1/t
    return integrate(integrand, 1, x)
