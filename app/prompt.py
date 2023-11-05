from app import speed
import time, os
import msvcrt


def cls():
    time.sleep(speed)
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def anyInput():   
    if os.name == "nt":
        print("Press any key")
        msvcrt.getch()
    else:
        print("key not supported")

def getKey():
    if os.name == "nt":
        moveCheck = msvcrt.getch()
        if moveCheck == b'\xe0':
            secondMoveCheck = msvcrt.getch()
            if secondMoveCheck == b'H':
                return "w"
            elif secondMoveCheck == b'P':
                return "s"
            elif secondMoveCheck == b'K':
                return "a"
            elif secondMoveCheck == b'M':
                return "d"
        moveCheck = moveCheck.decode("utf-8").lower()
        if (moveCheck == "a") or (moveCheck == "s") or (moveCheck == "d") or (moveCheck == "w"):
            return moveCheck
    else:
        print("key not supported")

def isTriggered():
    if os.name == "nt":
        return msvcrt.kbhit()
    else:
        print("key not supported")
    
def yesNo():
    if os.name == "nt":
        try:
            if msvcrt.getch().decode("utf-8").lower() == "n":
                return True
        except Exception:
            return False
    else:
        print("key not supported")
