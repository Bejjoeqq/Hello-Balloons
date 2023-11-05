from app.prompt import anyInput, yesNo
from app.start import play
from app.guide import info
from app.map import getMap
from app.guide import homeMenu
from pysharedoscom import menu

#replace this to your bot
from app.bot.bot_bejjo_v1 import checkBot, NAME 
# from app.bot.bot_bejjo_v2 import checkBot 

def main():
    scores = []
    name = ""
    allScores = [10000, 6000, 3000, 1000]
    allNames = ["Pro(Computer)", "Advance(Computer)", "Intermediate(Computer)", "Novice(Computer)"]
    while True:
        menus = menu(homeMenu)
        if menus == 0:
            best = 0
            scores = []
            name = input("Your Name : ")
            while True:
                map = getMap()
                score = play(name, best, map)
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
            map = getMap()
            best = "999999+"
            play(NAME, best, map, checkBot)
            anyInput()
        if menus == 5:
            break

if __name__ == '__main__':
    main()
