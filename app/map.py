import random
from app.guide import hint

class Map:
    def __init__(self, map: list):
        if len(map)<10 and len(map[0]<20):
            raise ValueError("invalid map")
        self.map = map
        self.xmap = len(self.map[0])
        self.ymap = len(self.map)
        self.__buildBorder()
        self.map[2][10] = "$"

    def getMap(self) -> list:
        return self.map
    
    def __buildBorder(self):
        for top in range(0, self.xmap, 2):
            self.map[0][top] = "*"
        for right in range(self.ymap):
            self.map[right][self.xmap - 2] = "*"
        for bottom in range(0, self.xmap, 2):
            self.map[self.ymap - 1][bottom] = "*"
        for left in range(self.ymap):
            self.map[left][0] = "*"
            
    def printMap(self):
        for row in range(self.ymap):
            for column in range(self.xmap):
                print(self.map[row][column], end="")
            print("")
        hint()
        print("\nResize Your Command Prompt")
        
    def dropRandomDollar(self):
        self.map[random.randint(1, self.ymap - 2)][random.randint(2,(self.xmap - 4) / 2) * 2] = "$"
    
    def findLocationDollar(self) -> list:
        for row in range(self.ymap):
            for column in range(self.xmap):
                if self.map[row][column] == "$":
                    return row, column
        input("not found need check")
