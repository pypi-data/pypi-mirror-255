def root(num, nth=2):
    if nth % -2 != 0 and num < 0:
        return -(abs(num)**(1/nth))
    else:
        return num**(1/nth)+abs(num**(1/nth))-abs(num**(1/nth))
