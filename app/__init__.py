def statePoint():
    rage = 50
    point = 0
    eated = 0
    sp = 200
    # speed = 0.05
    speed = 0.01
    return rage, point, eated, sp, speed

def baseMap():
    xmap = 80
    ymap = 20
    return [[" " for xx in range(xmap)] for xx in range(ymap)]