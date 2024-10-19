from app.hero import Hero

NAME = "BejjoV1"

def checkBot(hero: Hero):
    move = hero.getMove()
    heroLoc = hero.getLocation()
    prev_move = move
    ybot, xbot = hero.findLocationDollar()
    key = "asdw"

    if move == "a":
        if xbot - heroLoc[0] < 0:
            move = "a"
        elif ybot - heroLoc[1] > 0:
            move = "s"
        elif ybot - heroLoc[1] < 0:
            move = "w"
    elif move == "s":
        if xbot - heroLoc[0] < 0:
            move = "a"
        elif ybot - heroLoc[1] > 0:
            move = "s"
        elif xbot - heroLoc[0] > 0:
            move = "d"
    elif move == "d":
        if ybot - heroLoc[1] > 0:
            move = "s"
        elif xbot - heroLoc[0] > 0:
            move = "d"
        elif ybot - heroLoc[1] < 0:
            move = "w"
    elif move == "w":
        if xbot - heroLoc[0] < 0:
            move = "a"
        elif xbot - heroLoc[0] > 0:
            move = "d"
        elif ybot - heroLoc[1] < 0:
            move = "w"
    else:
        if xbot - heroLoc[0] < 0:
            move = "a"
        elif ybot - heroLoc[1] > 0:
            move = "s"
        elif xbot - heroLoc[0] > 0:
            move = "d"
        elif ybot - heroLoc[1] < 0:
            move = "w"

    retry = 10
    noOption = False
    while hero.spikeCheck(move):
        retry -= 1
        keys = key
        for mv in keys:
            if hero.spikeCheck(mv):
                key = key.replace(mv, "")
            if not hero.spikeCheck(mv):
                if mv == "a" and xbot - heroLoc[0] <= 0:
                    move = "a"
                    if prev_move == "d":
                        move = "d"
                    break
                elif mv == "s" and ybot - heroLoc[1] >= 0:
                    move = "s"
                    if prev_move == "w":
                        move = "w"
                    break
                elif mv == "d" and xbot - heroLoc[0] >= 0:
                    move = "d"
                    if prev_move == "a":
                        move = "a"
                    break
                elif mv == "w" and ybot - heroLoc[1] <= 0:
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