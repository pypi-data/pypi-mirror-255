def quad(a, b, c):
    if a == 0:
        raise ZeroDivisionError
    else:
        quad.delta = b**2 - 4*a*c
        if a + b + c == 0:
            if quad.delta == 0:
                quad.x0 = -b/(2*a)
                if a > 0:
                    signa = "+"
                else:
                    signa = "-"
                return f"a = {a} ; b = {b} ; c = {c}\na + b + c = 0\nx1 = 1\nx2 = c/a = {c}/{a} = {quad.x0}\n\n\nx      | -∞      x0     +∞ |\n————————————————————————————\nP(x)   |    {signa}    0    {signa}    |"
            else:
                quad.x1 = 1
                quad.x2 = c/a
                if a > 0:
                    signa = "+"
                    sign_a = "-"
                else:
                    signa = "-"
                    sign_a = "+"
                if quad.x1 > quad.x2:
                    return f"a = {a} ; b = {b} ; c = {c}\na + b + c = 0\nx1 = 1\nx2 = c/a = {c}/{a} = {quad.x2}\n\n\nx      | -∞     x2         x1     +∞ |\n——————————————————————————————————————\nP(x)   |    {signa}    0    {sign_a}    0    {signa}    |"
                else:
                    return f"a = {a} ; b = {b} ; c = {c}\na + b + c = 0\nx1 = 1\nx2 = c/a = {c}/{a} = {c/a}\n\n\nx      | -∞     x1         x2     +∞ |\n——————————————————————————————————————\nP(x)   |    {signa}    0    {sign_a}    0    {signa}    |"
        elif a - b + c == 0:
            if quad.delta == 0:
                quad.x0 = -b/(2*a)
                if a > 0:
                    signa = "+"
                else:
                    signa = "-"
                return f"a = {a} ; b = {b} ; c = {c}\na - b + c = 0\nx1 = -1\nx2 = -c/a = {-c}/{a} = {quad.x0}\n\n\nx      | -∞      x0     +∞ |\n————————————————————————————\nP(x)   |    {signa}    0    {signa}    |"
            else:
                quad.x1 = -1
                quad.x2 = -c/a
            if a > 0:
                signa = "+"
                sign_a = "-"
            else:
                signa = "-"
                sign_a = "+"
            if quad.x1 > quad.x2:
                return f"a = {a} ; b = {b} ; c = {c}\na - b + c = 0\nx1 = -1\nx2 = -c/a = {-c}/{a} = {quad.x2}\n\n\nx      | -∞     x2         x1     +∞ |\n——————————————————————————————————————\nP(x)   |    {signa}    0    {sign_a}    0    {signa}    |"
            else:
                return f"a = {a} ; b = {b} ; c = {c}\na - b + c = 0\nx1 = -1\nx2 = -c/a = {-c}/{a} = {quad.x2}\n\n\nx      | -∞     x1         x2     +∞ |\n——————————————————————————————————————\nP(x)   |    {signa}    0    {sign_a}    0    {signa}    |"
        elif quad.delta > 0:
            quad.x1 = (-b - quad.delta**(1/2))/(2*a)
            quad.x2 = (-b + quad.delta**(1/2))/(2*a)
            if a > 0:
                signa = "+"
                sign_a = "-"
            else:
                signa = "-"
                sign_a = "+"
            if quad.x1 > quad.x2:
                return f"a = {a} ; b = {b} ; c = {c}\nΔ = b² - 4ac\nΔ = {b}² - 4 × {a} × {c}\nΔ = {b**2} - {4*a*c}\nΔ = {quad.delta}\nx1 = (-b - √Δ) / 2a = ({-b} - √{quad.delta}) / (2 × {a}) = {quad.x1}\nx2 = (-b + √Δ) / 2a = ({-b} + √{quad.delta}) / (2 × {a}) = {quad.x2}\n\n\nx      | -∞     x2         x1     +∞ |\n——————————————————————————————————————\nP(x)   |    {signa}    0    {sign_a}    0    {signa}    |"
            else:
                return f"a = {a} ; b = {b} ; c = {c}\nΔ = b² - 4ac\nΔ = {b}² - 4 × {a} × {c}\nΔ = {b**2} - {4*a*c}\nΔ = {quad.delta}\nx1 = (-b - √Δ) / 2a = ({-b} - √{quad.delta}) / (2 × {a}) = {quad.x1}\nx2 = (-b + √Δ) / 2a = ({-b} + √{quad.delta}) / (2 × {a}) = {quad.x2}\n\n\nx      | -∞     x1         x2     +∞ |\n——————————————————————————————————————\nP(x)   |    {signa}    0    {sign_a}    0    {signa}    |"
        elif quad.delta == 0:
            quad.x0 = -b/(2*a)
            if a > 0:
                signa = "+"
            else:
                signa = "-"
            return f"a = {a} ; b = {b} ; c = {c}\nΔ = b² - 4ac\nΔ = {b}² - 4 × {a} × {c}\nΔ = {b**2} - {4*a*c}\nΔ = {quad.delta}\nx0 = -b / 2a = ({-b} / (2 × {a}) = {quad.x0}\n\n\nx      | -∞      x0     +∞ |\n————————————————————————————\nP(x)   |    {signa}    0    {signa}    |"
        else:
            if a > 0:
                signa = "+"
            else:
                signa = "-"
            return f"a = {a} ; b = {b} ; c = {c}\nΔ = b² - 4ac\nΔ = {b}² - 4 × {a} × {c}\nΔ = {b**2} - {4*a*c}\nΔ = {quad.delta} < 0\n\n\nx      | -∞         +∞ |\n———————————————————————\nP(x)   |       {signa}       |"
