def lcm(a:int,b:int):
    from .gcd import gcd
    return abs(a*b) // gcd(a,b)
