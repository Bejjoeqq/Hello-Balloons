import time, os, sys

from app import speed

if os.name != "nt":
    import termios,tty,select
else:
    import msvcrt


def cls():
    time.sleep(speed)
    if os.name != "nt":
        os.system("clear")
    else:
        os.system("cls")


def anyInput():
    if os.name != "nt":
        print("Press any key")
        sys.stdin.read(1)
    else:
        print("Press any key")
        msvcrt.getch()


def getKey():
    if os.name != "nt":
        raise NotImplementedError("This function is not implemented yet.")
    else:
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
        if moveCheck in ("a", "s", "d", "w"):
            return moveCheck


def isTriggered():
    if os.name != "nt":
        raise NotImplementedError("This function is not implemented yet.")
    else:
        return msvcrt.kbhit()


def yesNo():
    if os.name != "nt":
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            response = sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return response == "n"
    else:
        try:
            if msvcrt.getch().decode("utf-8").lower() == "n":
                return True
        except Exception:
            return False
