def limit(func, approaching, side="+"):
    k = 1e16
    if approaching == float('inf'):
        approaching = 99999999999
    else:
        approaching = -99999999999
    if side == "+":
        while True:
            try:
                result = func(approaching+1/k)
                break
            except:
                k = k // 10
        if result >= 1e5:
            return float('inf')
        elif result <= -1e5:
            return float('-inf')
        else:
            return result
    else:
        while True:
            try:
                result = func(approaching-1/k)
                break
            except:
                k = k // 10
        if result >= 1e5:
            return float('inf')
        elif result <= -1e5:
            return float('-inf')
        else:
            return result