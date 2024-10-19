from app.map import Map

class Hero(Map):
    def __init__(self, map: list):
        if map[2][4] != " ":
            raise ValueError("invalid coordinate")
        super().__init__(map)
        self.x = 4
        self.y = 2
        self.map[self.y][self.x] = "O"
        self.currentMove = ""

    def getLocation(self) -> list:
        return [self.x, self.y]

    def getMove(self) -> str:
        return self.currentMove
    
    def setMove(self, move: str):
        self.currentMove = move

    def __updateMove(self, item: str):
        if self.currentMove == "a":
            self.map[self.y][self.x] = item
            self.x -= 2
            self.map[self.y][self.x] = "O"
        elif self.currentMove == "s":
            self.map[self.y][self.x] = item
            self.y += 1
            self.map[self.y][self.x] = "O"
        elif self.currentMove == "d":
            self.map[self.y][self.x] = item
            self.x += 2
            self.map[self.y][self.x] = "O"
        elif self.currentMove == "w":
            self.map[self.y][self.x] = item
            self.y -= 1
            self.map[self.y][self.x] = "O"
    
    def __moveCheck(self, item: str):
        if self.currentMove == "a":
            return self.map[self.y][self.x - 2] == item
        elif self.currentMove == "s":
            return self.map[self.y + 1][self.x] == item
        elif self.currentMove == "d":
            return self.map[self.y][self.x + 2] == item
        elif self.currentMove == "w":
            return self.map[self.y - 1][self.x] == item
        
    def __nextCheck(self, item: str, move: str):
        if move == "a":
            return self.map[self.y][self.x - 2] == item
        elif move == "s":
            return self.map[self.y + 1][self.x] == item
        elif move == "d":
            return self.map[self.y][self.x + 2] == item
        elif move == "w":
            return self.map[self.y - 1][self.x] == item
    
    def move(self) -> list:
        if self.__moveCheck("$"):
            self.__updateMove("*")
            return [True, True]
        elif self.__moveCheck("*"):
            return [False, False]
        self.__updateMove(" ")
        return [True, False]
    
    def spikeCheck(self, move: str) -> bool:
        return self.__nextCheck("*", move)
    
    def eatCheck(self, move: str) -> bool:
        return self.__nextCheck("$", move)
