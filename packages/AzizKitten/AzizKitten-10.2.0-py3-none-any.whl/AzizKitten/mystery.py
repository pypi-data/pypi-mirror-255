def mystery():
    from random import randint, choice
    ch = 0
    while ch == 0:
        ch = 1
        select = int(input("---------- 1: Easy Level ----------\n---------- 2: Meduim Level ----------\n---------- 3: Hard Level ----------\nSelect your level:\n>>    "))
        attempt = 0
        if select == 1:
            guess = randint(0, 100)
            data = int(input("Guess the number from 0 -> 100:\n>>    "))
            for i in range(15):
                if data == guess:
                    attempt += 1
                    print("YOU GOT IT IN", attempt, "attempts")
                    break
                elif data > guess:
                    attempt += 1
                    count = 15 - attempt
                    print(count, "attempts left.")
                    data = int(input("less\n>>    "))
                elif data < guess:
                    attempt += 1
                    count = 15 - attempt
                    print(count, "attempts left.")
                    data = int(input("more\n>>    "))
                if attempt == 14:
                    if data != guess:
                        print("Failed :( try again later...")
                        break
        elif select == 2:
            guess = randint(0, 1000)
            data = int(input("Guess the number from 0 -> 1000:\n>>    "))
            for i in range(10):
                if data == guess:
                    attempt += 1
                    print("YOU GOT IT IN", attempt, "attempts")
                    break
                elif data > guess:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    data = int(input("less\n>>    "))
                elif data < guess:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    data = int(input("more\n>>    "))
                if attempt == 9:
                    if data != guess:
                        print("Failed :( try again later...")
                        break
        elif select ==3:
            guess = randint(10, 100)
            chr = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
            char = choice(chr)
            data = int(input("Guess the number from 10 -> 100:\n>>    "))
            datach = str(input("Guess the character from a -> z:\n>>    "))
            for i in range(10):
                datach = datach.lower()
                if data == guess and datach == char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("YOU GOT IT IN", attempt, "attempts")
                    break
                elif data == guess and datach > char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Number is correct. Character is before")
                    datach = str(input("character is before\n>>    "))
                    datach = datach.lower()
                elif data == guess and datach < char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Number is correct. Character is after")
                    datach = str(input("character is after\n>>    "))
                    datach = datach.lower()
                elif data > guess and datach == char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print ("Character is correct. Number is less")
                    data = int(input("number is less\n>>    "))
                elif data > guess and datach > char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Number is less. Character is before")
                    data = int(input("number is less\n>>    "))
                    datach = str(input("character is before\n>>    "))
                    datach = datach.lower()
                elif data > guess and datach < char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Number is less. Character is after")
                    data = int(input("number is less\n>>    "))
                    datach = str(input("character is after\n>>    "))
                    datach = datach.lower()
                elif data < guess and datach == char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Character is correct. Number is more")
                    data = int(input("number is more\n>>    "))
                elif data < guess and datach < char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Number is more. Character is after")
                    data = int(input("number is more\n>>    "))
                    datach = str(input("character is after\n>>    "))
                    datach = datach.lower()
                elif data < guess and datach > char:
                    attempt += 1
                    count = 10 - attempt
                    print(count, "attempts left.")
                    print("Number is more. Character is before")
                    data = int(input("number is more\n>>    "))
                    datach = str(input("character is before\n>>    "))
                    datach = datach.lower()
                if attempt == 9:
                    if data != guess or datach != char:
                        print("Failed :( try again later...")
                        break
        else:
            print("error at choicing level :(")
            ch = 0