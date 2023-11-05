from app.map import borderMap, mapCheck, printMap
from app.hero import findDollar, eatCheck, moveHero, dropDollar
from app.guide import header
from app.prompt import cls, getKey, isTriggered
from app import state

#replace this to your bot
from app.bot.bot_bejjo_v1 import checkBot 
# from app.bot.bot_bejjo_v2 import checkBot 

def play(name, best, map, bot=False):
    map, rage, point, eated, sp, move, hero = state(map)
    while True:
        cls()
        header(point, rage, sp, name, best, eated, map)
        ybot, xbot = findDollar(map)
        print(f"Location : {xbot}, {ybot}")
        if rage != 0:
            rage -= 1
        if sp != 0:
            sp -= 1

        if bot:
            move = checkBot(move, map, hero)
        else:
            if isTriggered():
                move = getKey()

        check = mapCheck(move, map, hero)
        if check:
            printMap(map)
            break

        check = eatCheck(move, map, hero)
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
        map, hero = moveHero(move, check, map, hero)
        printMap(map)
    return point
