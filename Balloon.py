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

        print(f"Point : {point}\tRage : {rage}\tName : {name}\tBest Score : {best}")
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
def main():
    name=""
    best=0
    scores=[]
    lead={
        "Pro":1000,
        "Advance":600,
        "Intermediate":300,
        "Novice":100
    }
    while True:
        cls()
        print("Hello Ballons\n-------------")
        print("1.Play\n2.Recent Score\n3.Leaderboard\n?.Details\n4.Exit")
        print("Choice : ")
        asd = msvcrt.getch().decode("utf-8")
        if asd=="1":
            cls()
            best = 0
            scores=[]
            name = input("Your Name : ")
            while True:
                global xmap,ymap,x,y,map

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
                print("Game Over")
                print("Press [n] to back")
                if msvcrt.getch().decode("utf-8").lower() == "n":
                    break
        elif asd=="2":
            print(name,scores)
            msvcrt.getch()
        elif asd=="3":
            for y,x in enumerate(sorted(lead, key=lead.get, reverse=True)):
                print(y+1,x, lead[x])
            msvcrt.getch()
        elif asd=="4":
            break
        lead[name] = best

if __name__ == '__main__':
    main()
