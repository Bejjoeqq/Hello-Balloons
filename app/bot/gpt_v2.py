from app.hero import Hero

NAME = "GPTBotV2"

# We'll introduce a new variable to track the previous move
previous_move = ""

def checkBot(hero: Hero):
    global previous_move

    # Get the current location of the bot and the dollar
    heroLoc = hero.getLocation()
    ybot, xbot = hero.findLocationDollar()

    # Calculate the directional difference to the dollar
    y_diff = ybot - heroLoc[1]
    x_diff = xbot - heroLoc[0]

    # Determine the most optimal move
    move = ""
    
    # Prioritize horizontal or vertical movement based on the position of the dollar
    if abs(x_diff) > abs(y_diff):
        if x_diff > 0:
            move = "d"  # Move right
        else:
            move = "a"  # Move left
    else:
        if y_diff > 0:
            move = "s"  # Move down
        else:
            move = "w"  # Move up
    
    # Avoid repeating the previous move in the opposite direction (avoiding w-s or s-w loops)
    if (previous_move == "w" and move == "s") or (previous_move == "s" and move == "w"):
        # Choose a new move when stuck in an up-down loop
        if x_diff != 0:  # Try horizontal movement instead
            move = "d" if x_diff > 0 else "a"
        else:
            move = "w" if previous_move == "s" else "s"  # Force a different vertical move
    
    # Avoid spikes if the desired move leads to one
    if hero.spikeCheck(move):
        # Try alternative directions
        alternatives = ["w", "a", "s", "d"]
        alternatives.remove(move)  # Exclude the current move

        # Find a valid direction that avoids spikes
        for alt_move in alternatives:
            if not hero.spikeCheck(alt_move):
                move = alt_move
                break

    # Save the current move as the previous move for the next cycle
    previous_move = move

    return move
