import random
from app.guide import hint
from colorama import Fore, Style

class Map:
    def __init__(self, map: list):
        if len(map)<10 and len(map[0]<20):
            raise ValueError("invalid map")
        self.map = map
        self.xmap = len(self.map[0])
        self.ymap = len(self.map)
        self.__buildBorder()
        self.yLastDollarCoor = 2
        self.xLastDollarCoor = 10
        self.map[self.yLastDollarCoor][self.xLastDollarCoor] = "$"

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
                char = self.map[row][column]
                if char == '$':
                    print(Fore.RED + char + Style.RESET_ALL, end="")
                else:
                    print(char, end="")
            print("")
        hint()
        print("\nResize Your Command Prompt")
        
    def dropRandomDollar(self):
        yDollarCoor = random.randint(1, self.ymap - 2)
        xDollarCoor = random.randint(2,(self.xmap - 4) / 2) * 2
        if xDollarCoor == self.xLastDollarCoor and yDollarCoor == self.yLastDollarCoor:
            yDollarCoor = random.randint(1, self.ymap - 2)
            xDollarCoor = random.randint(2,(self.xmap - 4) / 2) * 2
        self.map[yDollarCoor][xDollarCoor] = "$"
        self.xLastDollarCoor = xDollarCoor
        self.yLastDollarCoor = yDollarCoor

    def getLocationDollar(self) -> list:
        return [self.yLastDollarCoor, self.xLastDollarCoor]
    
    def findLocationDollar(self) -> list:
        for row in range(self.ymap):
            for column in range(self.xmap):
                if self.map[row][column] == "$":
                    return row, column
        self.printMap()
        input("not found need check")
