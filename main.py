from app.prompt import anyInput, yesNo
from app.start import play
from app.guide import info
from app.map import getMap
from app.guide import homeMenu, allScores, allScores
from pysharedoscom import menu

def main():
    scores = []
    name = ""
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
        if menus == 1:
            print("\nLast Played\n-----------")
            print(name, ",".join(scores))
            anyInput()
        if menus == 2:
            print("\nLocal Rank\n----------")
            for y, x in enumerate(sorted(allScores, reverse=True)):
                p = allScores.index(x)
                print(f"{y+1}. {allScores[p]} : {allScores[p]}")
            anyInput()
        if menus == 3:
            info()
            anyInput()
        if menus == 4:
            map = getMap()
            name = "bot"
            best = "999999+"
            play(name, best, map, True)
            anyInput()
        if menus == 5:
            break

if __name__ == '__main__':
    main()
