homeMenu = ["Play","Recent Score","Leaderboard","Details","Bot","Exit"]

def hint():
    print("A : Left\tS : Down\tD : Right\tW : Up")

def info():
    print("\nInformation\n-----------")
    print("Dont hit the spike!!")
    print(
        "When the balloon hit the dollars, it will spawn a spike before\nExample : ")
    print("\n* * *          * * *")
    print("O $     ->     * O")
    print("* * *          * * *\n")
    print("\nMove Keys :")
    hint()

def header(point, rage, sp, name, best, eated, map):
    print(f"Point($) : {point}\tRage : {rage}\t Time : {sp}\tName : {name}\tBest Score : {best}")
    print(f"Spike : {sum(map, []).count('*') - 116}\tEated : {eated}\t", end="")