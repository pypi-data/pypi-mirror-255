def factorial(n: int):
    if n < 0 or type(n) is not int:
        raise ValueError("Value input must be positive integer.")
    ans = 1
    for i in range(1,n+1):
        ans *= i
    return ans
