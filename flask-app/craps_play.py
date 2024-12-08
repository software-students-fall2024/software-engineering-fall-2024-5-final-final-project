from craps_func import *

balance = 100000.00
game = input("Welcome, lets start. \nWhat kind of bet would you like to play (p,d,b,l)? ")
while game not in ["p", "d", "l", "b"]:
    game = input("Please choose from (p,d,b,l): ")

cont = True
while balance > -1000 and cont:
    print("Balance:", balance)
    bet = -1
    while bet < 0:
        try:
            bet = float(input("How much would you like to bet? "))
        except:
            print("Please enter a numerical value!")

    if game == 'p':
        rolls, outcome = linebet(True)
        print("Here were the rolls:")
        for r in rolls:
            print(r)
        if outcome == 'w':
            balance += bet
            print("You win!")
        elif outcome == 'l':
            balance -= bet
            print("You lose!")
        else:
            print("Tie! The first roll was a 12")
        print("New Balance:", balance)

    elif game == 'd':
        rolls, outcome = linebet(False)
        print("Here were the rolls:")
        for r in rolls:
            print(r)
        if outcome == 'w':
            balance += bet
            print("You win!")
        elif outcome == 'l':
            balance -= bet
            print("You lose!")
        else:
            print("Tie! The first roll was a 12")
        print("New Balance:", balance)

    elif game == 'b' or game == 'l':
        place = -1
        while place not in [4, 5, 6, 8, 9, 10]:
            try:
                place = int(input("Which place would you like to buy/lay (4, 5, 6, 8, 9, or 10)? "))
            except:
                print("Please enter a numerical value!")
        rolls, outcome, odds = buybet(True, place) if game == 'b' else buybet(False, place)
        print("The odds are:", odds)
        print("Here are the rolls:")
        for r in rolls:
            print(r)
        if outcome == 'w':
            print("You win!")
            balance += odds * bet
        else:
            # no tie in this bet mode
            print("You lose!")
            balance -= bet
        print("New Balance:", balance)

    response = "Hi"
    while(response not in ["yes", "no", 'y', 'n']):
        response = input("Would you like to play again? Please enter yes or no: ").lower()
    
    if response in ["yes", "y"]:
        cont = True
        game = 'z'
        while game not in ["p", "d", "l", "b"]:
            game = input("Please choose from (p,d,b,l): ")
    else:
        cont = False
        break  # just break for simplicity

    print()
    print()