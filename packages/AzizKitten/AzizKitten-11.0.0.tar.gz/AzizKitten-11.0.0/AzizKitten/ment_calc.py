def ment_calc():
    from time import sleep
    from threading import Thread
    from random import randint,choice
    t = 1
    print('You must get most points in mental calculation in 30 secondes')
    sleep(5)
    def SpeedRun():
        p = 0
        while t > 0:
            f = randint(0,10)
            s = randint(0,10)
            rand = ['add', 'sub', 'mult', 'div']
            o = choice(rand)
            if o == 'add':
                data = f + s
                ans = int(input(str(f)+' + '+str(s)+' = ?\n>>   '))
                if ans == data:
                    print('Correct!')
                    p += 1
                else:
                    print('Fail!')
            if o == 'sub':
                data = f - s
                ans = int(input(str(f)+' - '+str(s)+' = ?\n>>   '))
                if ans == data:
                    print('Correct!')
                    p += 1
                else:
                    print('Fail!')
            if o == 'mult':
                data = f * s
                ans = int(input(str(f)+' * '+str(s)+' = ?\n>>   '))
                if ans == data:
                    print('Correct!')
                    p += 1
                else:
                    print('Fail!')
            if o == 'div':
                s = randint(1,5)
                if s == 1:
                    f = randint(0,10)
                elif s == 2:
                    choices = [0,2,4,6,8,10]
                    f = choice(choices)
                elif s == 3:
                    choices = [0,3,6,9]
                    f = choice(choices)
                elif s == 4:
                    choices = [0,4,8]
                    f = choice(choices)
                elif s == 5:
                    choices = [0,5,10]
                    f = choice(choices)
                data =  f / s
                ans = int(input(str(f)+' / '+str(s)+' = ?\n>>   '))
                if ans == data:
                    print('Correct!')
                    p += 1
                else:
                    print('Fail!')
        if t == 0:
            print('Time is up!\nYour score is',p)
    Thread(target=SpeedRun).start()
    sleep(30)
    t = 0