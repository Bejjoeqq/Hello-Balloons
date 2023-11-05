from app.hero import findDollar
from app.map import mapCheck

def checkBot(move, map, hero):
    prev_move = move
    ybot, xbot = findDollar(map)
    key = "asdw"

    if move == "a":
        if xbot - hero[0] < 0:
            move = "a"
        elif ybot - hero[1] > 0:
            move = "s"
        elif ybot - hero[1] < 0:
            move = "w"
    elif move == "s":
        if xbot - hero[0] < 0:
            move = "a"
        elif ybot - hero[1] > 0:
            move = "s"
        elif xbot - hero[0] > 0:
            move = "d"
    elif move == "d":
        if ybot - hero[1] > 0:
            move = "s"
        elif xbot - hero[0] > 0:
            move = "d"
        elif ybot - hero[1] < 0:
            move = "w"
    elif move == "w":
        if xbot - hero[0] < 0:
            move = "a"
        elif xbot - hero[0] > 0:
            move = "d"
        elif ybot - hero[1] < 0:
            move = "w"
    else:
        if xbot - hero[0] < 0:
            move = "a"
        elif ybot - hero[1] > 0:
            move = "s"
        elif xbot - hero[0] > 0:
            move = "d"
        elif ybot - hero[1] < 0:
            move = "w"

    retry = 10
    noOption = False
    while mapCheck(move, map, hero):
        retry -= 1
        keys = key
        for mv in keys:
            if mapCheck(mv, map, hero):
                key = key.replace(mv, "")
            if not mapCheck(mv, map, hero):
                if mv == "a" and xbot - hero[0] <= 0:
                    move = "a"
                    if prev_move == "d":
                        move = "d"
                    break
                elif mv == "s" and ybot - hero[1] >= 0:
                    move = "s"
                    if prev_move == "w":
                        move = "w"
                    break
                elif mv == "d" and xbot - hero[0] >= 0:
                    move = "d"
                    if prev_move == "a":
                        move = "a"
                    break
                elif mv == "w" and ybot - hero[1] <= 0:
                    move = "w"
                    if prev_move == "s":
                        move = "s"
                    break
        if retry == 0:
            noOption = True
            break

    if noOption:
        for mvs in key:
            move = mvs

    return move