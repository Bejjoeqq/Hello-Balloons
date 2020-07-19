import os,msvcrt,random
xmap = 80
ymap = 20
x = 4
y = 2
map = [[" " for x in range(xmap)] for x in range(ymap)]

def cls():
    if os.name=="nt":
        os.system("cls")
    else:
        os.system("clear")
def borderMap():
    for top in range(0,xmap,2):
        map[0][top] = "*"
    for right in range(ymap):
        map[right][xmap-2] = "*"
    for bottom in range(0,xmap,2):
        map[ymap-1][bottom] = "*"
    for left in range(ymap):
        map[left][0] = "*"
def printMap():
    for row in range(ymap):
        for column in range(xmap):
            print(map[row][column],end="")
        print("")
    infor()
    print("\nResize Your Command Prompt")
def moveHero(move,eat):
    global y,x
    if move == "a":
        if eat:
            map[y][x] = "*"
            x-=2
            map[y][x] = "O"
        else:
            map[y][x] = " "
            x-=2
            map[y][x] = "O"
    elif move == "s":
        if eat:
            map[y][x] = "*"
            y+=1
            map[y][x] = "O"
        else:
            map[y][x] = " "
            y+=1
            map[y][x] = "O"
    elif move == "d":
        if eat:
            map[y][x] = "*"
            x+=2
            map[y][x] = "O"
        else:
            map[y][x] = " "
            x+=2
            map[y][x] = "O"
    elif move == "w":
        if eat:
            map[y][x] = "*"
            y-=1
            map[y][x] = "O"
        else:
            map[y][x] = " "
            y-=1
            map[y][x] = "O"
    return move
def mapCheck(move):
    if move == "a":
        return (map[y][x-2] != " ") and (map[y][x-2] != "$")
    elif move == "s":
        return (map[y+1][x] != " ") and (map[y+1][x] != "$")
    elif move == "d":
        return (map[y][x+2] != " ") and (map[y][x+2] != "$")
    elif move == "w":
        return (map[y-1][x] != " ") and (map[y-1][x] != "$")
def eatCheck(move):
    if move == "a":
        return (map[y][x-2] == "$")
    elif move == "s":
        return (map[y+1][x] == "$")
    elif move == "d":
        return (map[y][x+2] == "$")
    elif move == "w":
        return (map[y-1][x] == "$")
def dropDollar():
    map[random.randint(1,ymap-2)][random.randint(2,(xmap-4)/2)*2] = "$"
def play(name,best):
    rage = 50
    point = 0
    map[2][10] = "$"
    move = ""
    borderMap()
    while True:

        cls()

        print(f"Point($) : {point}\tRage : {rage}\tName : {name}\tBest Score : {best}")
        if rage != 0:
            rage-=1

        if msvcrt.kbhit():
            moveCheck = msvcrt.getch().decode("utf-8").lower()
            if (moveCheck == "a") or (moveCheck == "s") or (moveCheck == "d") or (moveCheck == "w"):
                move = moveCheck

        check = mapCheck(move)
        if check:
            break

        check2 = eatCheck(move)
        moveHero(move,check2)
        if check2:
            point += 20
            point += rage
            rage = 50
            dropDollar()

        printMap()
    return point
def infor():
    print("A : Left\tS : Down\tD : Right\tW : Up")
def findDollar():
    for row in range(ymap):
        for column in range(xmap):
            if map[row][column]=="$":
                return row,column
mark2=False
def checkBot(move):
    global mark2
    ybot,xbot = findDollar()
    key=["da","sw"]
    print(xbot,ybot)
    if mark2:
        if move=="a":
            if xbot-x<0:
                move = "a"
            elif ybot-y>0:
                move = "s"
            elif ybot-y<0:
                move = "w"
        elif move=="s":
            if xbot-x<0:
                move = "a"
            elif ybot-y>0:
                move = "s"
            elif xbot-x>0:
                move = "d"
        elif move=="d":
            if ybot-y>0:
                move = "s"
            elif xbot-x>0:
                move = "d"
            elif ybot-y<0:
                move = "w"
        elif move=="w":
            if xbot-x<0:
                move = "a"
            elif xbot-x>0:
                move = "d"
            elif ybot-y<0:
                move = "w"
    else:
        if xbot-x<0:
            move = "a"
        elif ybot-y>0:
            move = "s"
        elif xbot-x>0:
            move = "d"
        elif ybot-y<0:
            move = "w"
    mark2=False
    if mapCheck(move):
        mark=0
        if move=="d" or move=="a":
            mark=1
        for mv in key[mark]:
            if mapCheck(mv)==False:
                if mv=="a" and xbot-x<=0:
                    move="a"
                elif mv=="s" and ybot-y>=0:
                    move="s"
                elif mv=="d" and xbot-x>=0:
                    move="d"
                elif mv=="w" and ybot-y<=0:
                    move="w"
                mark2=True

    return move
def bot(name="Bot",best="9999"):
    rage = 50
    point = 0
    map[2][10] = "$"
    move = ""
    borderMap()
    while True:

        cls()

        print(f"Point($) : {point}\tRage : {rage}\tName : {name}\tBest Score : {best}")
        if rage != 0:
            rage-=1

        move = checkBot(move)

        check = mapCheck(move)
        if check:
            break

        check2 = eatCheck(move)
        moveHero(move,check2)
        if check2:
            point += 20
            point += rage
            rage = 50
            dropDollar()

        printMap()
    return point
def main():
    global xmap,ymap,x,y,map
    scores=[]
    name=""
    allscores = [1000,600,300,100]
    allnames = ["Pro(Computer)","Advance(Computer)","Intermediate(Computer)","Novice(Computer)"]
    while True:
        cls()
        print("Hello Ballons\n-------------")
        print("1.Play\n2.Recent Score\n3.Leaderboard\n4.Details\n5.Bot\n6.Exit")
        print("Choice : ")
        asd = msvcrt.getch().decode("utf-8")
        if asd=="1":
            cls()
            best = 0
            scores=[]
            name = input("Your Name : ")
            while True:
                xmap = 80
                ymap = 20
                x = 4
                y = 2
                map = [[" " for x in range(xmap)] for x in range(ymap)]
                map[y][x] = "O"

                score = play(name,best)
                if score>best:
                    best=score
                scores.append(score)

                printMap()
                print("\nGame Over")
                print("Press [n] to back")
                if msvcrt.getch().decode("utf-8").lower() == "n":
                    break
            allscores.append(best)
            allnames.append(name)
        elif asd=="2":
            print("\nLast Played\n-----------")
            print(name,scores)
            print("Press any key")
            msvcrt.getch()
        elif asd=="3":
            print("\nLocal Rank\n----------")
            for y,x in enumerate(sorted(allscores,reverse=True)):
                p = allscores.index(x)
                print(f"{y+1}. {allscores[p]} : {allnames[p]}")
            print("Press any key")
            msvcrt.getch()
        elif asd=="4":
            print("\nInformation\n-----------")
            print("Dont hit the spike!!")
            print("When the balloon hit the dollars, it will spawn a spike before\nExample : ")
            print("\n* * *          * * *")
            print("O $     ->     * O")
            print("* * *          * * *\n")
            print("\nMove Keys :")
            infor()
            print("\nPress any key")
            msvcrt.getch()
        elif asd=="5":
            xmap = 80
            ymap = 20
            x = 4
            y = 2
            map = [[" " for x in range(xmap)] for x in range(ymap)]
            map[y][x] = "O"
            bot()
            printMap()
            msvcrt.getch()
        elif asd=="6":
            break

if __name__ == '__main__':
    main()
