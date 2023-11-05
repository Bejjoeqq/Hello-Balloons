from app.map import mapCheck, printMap
from app.hero import findDollar, eatCheck, moveHero, dropDollar
from app.guide import header
from app.prompt import cls, getKey, isTriggered
from app import state

def play(name, best, map, bot=None):
    map, rage, point, eated, sp, move, hero = state(map)
    while True:
        cls()
        header(point, rage, sp, name, best, eated, map)
        ybot, xbot = findDollar(map)
        print(f"Location : {xbot}, {ybot}")
        if sp == 0:
            printMap(map)
            break
        if rage != 0:
            rage -= 1
        if sp != 0:
            sp -= 1

        if bot:
            move = bot(move, map, hero)
        else:
            if isTriggered():
                move = getKey()

        check = mapCheck(move, map, hero)
        if check:
            printMap(map)
            break

        check = eatCheck(move, map, hero)
        map, hero = moveHero(move, check, map, hero)
        if check:
            point += 20
            point += rage + sp
            rage = 50
            if eated % 9 == 0:
                sp += 200
            if (sum(map, []).count('*') - 116) % 4 == 0:
                sp += 50
            eated += 1
            map = dropDollar(map)
        printMap(map)
    return point
