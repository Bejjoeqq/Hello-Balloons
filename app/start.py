from app.hero import Hero
from app.guide import header
from app.prompt import cls, getKey, isTriggered
from app import statePoint

def play(name, best, map, speed, bot=None):
    rage, point, eated, sp = statePoint()
    hero = Hero(map)
    while True:
        cls(speed)
        header(point, rage, sp, name, best, eated, map)
        yDollar, xDoollar = hero.getLocationDollar()
        print(f"Location : {xDoollar}, {yDollar}")
        if sp <= 0:
            hero.printMap()
            break
        if rage != 0:
            rage -= 1
        if sp != 0:
            # deduction = (point // 10000) + 1
            # sp -= deduction
            sp -= 1

        if bot:
            move = bot(hero)
            hero.setMove(move)
        else:
            if isTriggered():
                move = getKey()
                if move:
                    hero.setMove(move)

        safety, isEat = hero.move()
        if not safety:
            hero.printMap()
            break

        if isEat:
            point += 20
            point += rage + sp
            rage = 50
            if eated % 9 == 0:
                sp += 200
            if (sum(map, []).count('*') - 116) % 4 == 0:
                sp += 50
            eated += 1
            hero.dropRandomDollar()
        hero.printMap()
    return point
