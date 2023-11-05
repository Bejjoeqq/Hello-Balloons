from app.map import borderMap

x = 4
y = 2
rage = 50
point = 0
eated = 0
sp = 200
move = ""

def state(map):
    map = borderMap(map)
    map[2][10] = "$"
    map[y][x] = "O"
    return map, rage, point, eated, sp, move, [x, y]