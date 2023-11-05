from app.map import ymap, xmap
import random

def moveHero(move, eat, map, hero):
    if move == "a":
        if eat:
            map[hero[1]][hero[0]] = "*"
            hero[0] -= 2
            map[hero[1]][hero[0]] = "O"
        else:
            map[hero[1]][hero[0]] = " "
            hero[0] -= 2
            map[hero[1]][hero[0]] = "O"
    elif move == "s":
        if eat:
            map[hero[1]][hero[0]] = "*"
            hero[1] += 1
            map[hero[1]][hero[0]] = "O"
        else:
            map[hero[1]][hero[0]] = " "
            hero[1] += 1
            map[hero[1]][hero[0]] = "O"
    elif move == "d":
        if eat:
            map[hero[1]][hero[0]] = "*"
            hero[0] += 2
            map[hero[1]][hero[0]] = "O"
        else:
            map[hero[1]][hero[0]] = " "
            hero[0] += 2
            map[hero[1]][hero[0]] = "O"
    elif move == "w":
        if eat:
            map[hero[1]][hero[0]] = "*"
            hero[1] -= 1
            map[hero[1]][hero[0]] = "O"
        else:
            map[hero[1]][hero[0]] = " "
            hero[1] -= 1
            map[hero[1]][hero[0]] = "O"
    return map, hero

def eatCheck(move, map, hero):
    if move == "a":
        return (map[hero[1]][hero[0] - 2] == "$")
    elif move == "s":
        return (map[hero[1] + 1][hero[0]] == "$")
    elif move == "d":
        return (map[hero[1]][hero[0] + 2] == "$")
    elif move == "w":
        return (map[hero[1] - 1][hero[0]] == "$")
    
    
def dropDollar(map):
    map[random.randint(1, ymap - 2)][random.randint(2,(xmap - 4) / 2) * 2] = "$"
    return map

    
def findDollar(map):
    for row in range(ymap):
        for column in range(xmap):
            if map[row][column] == "$":
                return row, column
            