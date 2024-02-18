def sin(x, deg=False):
    from .factorial import factorial
    from .constants import pi
    if deg:
        x = pi*(x/180)
    ans = 0
    for n in range(30):
        coef = (-1)**n
        num = x**(2*n+1)
        den = factorial(2*n+1)
        ans += coef*num/den
    return ans
