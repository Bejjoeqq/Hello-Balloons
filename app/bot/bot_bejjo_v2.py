from app.hero import findDollar
from app.map import mapCheck
import random

NAME = "BejjoV2"
next_move=[]

def checkBot(map, hero):
    global next_move
    block_move=[]
    list_move="adsw"
    temp_hero = list(hero)
    ybot, xbot = findDollar(map)
    if next_move:
        return next_move.pop(0), next_move
    while True:
        if (xbot == temp_hero[0]) and (ybot == temp_hero[1]):
            break
        if (xbot - temp_hero[0] < 0) and ("a" not in block_move):
            move = "a"
        elif ybot - temp_hero[1] > 0 and ("s" not in block_move):
            move = "s"
        elif xbot - temp_hero[0] > 0 and ("d" not in block_move):
            move = "d"
        elif ybot - temp_hero[1] < 0 and ("w" not in block_move):
            move = "w"
        # else:
        #     if not mapCheck(move, map, temp_hero):
        #         next_move.append(move)
        #         break
        #     # move = random.choice(list_move.replace("".join(block_move),"")) 
        #     move = random.choice(list_move.replace(next_move[-1],"")) 
        #     del next_move[-1]

        print(list_move)
        input("tes")
        if mapCheck(move, map, temp_hero):
            block_move.append(move)
            list_move = list_move.replace(move,"")
            move = random.choice(list_move)
            continue
            # if mapCheck(move, map, temp_hero):
            #     nextm = list_move.replace(move,"")
            #     move = random.choice(nextm)
            #     if mapCheck(move, map, temp_hero):
            #         nextm = list_move.replace(move,"")
            #         move = random.choice(nextm)
            #         if mapCheck(move, map, temp_hero):
            #             print("kenak")
            #             input()
            #             if next_move:
            #                 if next_move[-1] == "a":
            #                     temp_hero[0] += 2
            #                 if next_move[-1] == "w":
            #                     temp_hero[1] += 1
            #                 if next_move[-1] == "d":
            #                     temp_hero[0] -= 2
            #                 if next_move[-1] == "s":
            #                     temp_hero[1] -= 1
            #                 block_move.append(next_move[-1])
            #                 del next_move[-1]
            #                 continue

        next_move.append(move)
        if move == "a":
            temp_hero[0] -= 2
        if move == "w":
            temp_hero[1] -= 1
        if move == "d":
            temp_hero[0] += 2
        if move == "s":
            temp_hero[1] += 1
        block_move=[]
        if len(next_move)>100:
            break
    return next_move.pop(0), next_move
