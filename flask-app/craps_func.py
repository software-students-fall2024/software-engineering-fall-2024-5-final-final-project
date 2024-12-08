"""
This file will create the basic functionalities for the craps game.
"""
from random import randint

# dictionary for returns of buy bets
odds = {
    4: 2/1,
    5: 3/2,
    6: 6/5,
    8: 6/5,
    9: 3/2,
    10: 2/1,
    -4: 1/2,
    -5: 2/3,
    -6: 5/6,
    -8: 5/6,
    -9: 2/3,
    -10: 1/2,
}

def linebet(win: bool):
    """
    This function is for 'line bets', either pass or don't pass.
    If the user placed a pass bet, then win should be true. If win is false,
    then the user placed a don't pass bet. The function returns a character (string),
    either w, l, or t if the user wins, loses, or ties (in the case of 12 on the
    first roll), and list of all rolls.
    """
    all_rolls = []
    roll = (randint(1, 6), randint(1, 6))
    total = sum(roll)
    all_rolls.append(f"{roll} = {total}")
    if total == 7 or total == 11:
        return (all_rolls, "w") if win else (all_rolls, "l")
    elif total == 2 or total == 3:
        return (all_rolls, "l") if win else (all_rolls, "w")
    elif total == 12:
        return all_rolls, "t"
    
    # set point
    point: int = total
    roll = (randint(1, 6), randint(1, 6))
    total = sum(roll)
    all_rolls.append(f"{roll} = {total}")
    while total != 7:
        # player now loses if a seven is rolled before the point (if a pass bet)
        if total == point:
            return (all_rolls, "w") if win else (all_rolls, "l")
        
        roll = (randint(1, 6), randint(1, 6))
        # all_rolls.append(roll)
        total = sum(roll)
        all_rolls.append(f"{roll} = {total}")
    
    # if while loop broken a seven was rolled
    return (all_rolls, "l") if win else (all_rolls, "w")

def buybet(win: bool, place: int):
    """
    """

    # determine odds
    payoutodds = odds[place] if win else odds[-place]
    all_rolls = []
    roll = (randint(1, 6), randint(1, 6))
    total = sum(roll)
    all_rolls.append(f"{roll} = {total}")
    while total != 7:
        if total == place:
            return (all_rolls, "w", payoutodds) if win else (all_rolls, "l", payoutodds)
        roll = (randint(1, 6), randint(1, 6))
        total = sum(roll)
        all_rolls.append(f"{roll} = {total}")
    
    # if while loop broken a seven was rolled
    return (all_rolls, "l", payoutodds) if win else (all_rolls, "w", payoutodds)
