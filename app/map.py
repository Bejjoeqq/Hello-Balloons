from app.guide import hint

xmap = 80
ymap = 20

def getMap():
    return [[" " for xx in range(xmap)] for xx in range(ymap)]

def borderMap(map):
    for top in range(0, xmap, 2):
        map[0][top] = "*"
    for right in range(ymap):
        map[right][xmap - 2] = "*"
    for bottom in range(0, xmap, 2):
        map[ymap - 1][bottom] = "*"
    for left in range(ymap):
        map[left][0] = "*"

    return map
        
def printMap(map):
    for row in range(ymap):
        for column in range(xmap):
            print(map[row][column], end="")
        print("")
    hint()
    print("\nResize Your Command Prompt")


def mapCheck(move, map, hero):
    if move == "a":
        return (map[hero[1]][hero[0] - 2] != " ") and (map[hero[1]][hero[0] - 2] != "$")
    elif move == "s":
        return (map[hero[1] + 1][hero[0]] != " ") and (map[hero[1] + 1][hero[0]] != "$")
    elif move == "d":
        return (map[hero[1]][hero[0] + 2] != " ") and (map[hero[1]][hero[0] + 2] != "$")
    elif move == "w":
        return (map[hero[1] - 1][hero[0]] != " ") and (map[hero[1] - 1][hero[0]] != "$")