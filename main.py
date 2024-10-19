from app.prompt import anyInput, yesNo
from app.start import play
from app.guide import info
from app import baseMap
from app.guide import homeMenu, speedLevel
from pysharedoscom import menu
from app.bot import getBot


def main():
    scores = []
    name = ""
    allScores = [10000, 6000, 3000, 1000]
    allNames = ["Pro(Computer)", "Advance(Computer)", "Intermediate(Computer)", "Novice(Computer)"]
    while True:
        menus = menu(homeMenu(), title="=+=+=+=+=+=+=+=", desc="=+=+=+=+=+=+=+=")
        if menus == 0:
            best = 0
            scores = []
            name = input("Your Name : ")
            speedIdx = menu(speedLevel(), title="=+=+=+=+=+=+=+=", desc="=+=+=+=+=+=+=+=")
            speed = [0.1, 0.05, 0.01]
            while True:
                map = baseMap()
                score = play(name, best, map, speed[speedIdx])
                if score > best:
                    best = score
                scores.append(score)
                print("\nGame Over")
                print("Press [n] to back")
                yes = yesNo()
                if yes:
                    break
            allScores.append(best)
            allNames.append(name)
        if menus == 1:
            print("\nLast Played\n-----------")
            print(name, scores)
            anyInput()
        if menus == 2:
            print("\nLocal Rank\n----------")
            for y, x in enumerate(sorted(allScores, reverse=True)):
                p = allScores.index(x)
                print(f"{y+1}. {allScores[p]} : {allNames[p]}")
            anyInput()
        if menus == 3:
            info()
            anyInput()
        if menus == 4:
            map = baseMap()
            best = "999999+"
            botMenu = getBot()
            botList = list(botMenu)
            botChoice = menu(botList, title="=+=+=+=+=+=+=+=", desc="=+=+=+=+=+=+=+=")
            play(botMenu[botList[botChoice]]["name"], best, map, 0.01, botMenu[botList[botChoice]]["func"])
            anyInput()
        if menus == 5:
            break

if __name__ == '__main__':
    main()
