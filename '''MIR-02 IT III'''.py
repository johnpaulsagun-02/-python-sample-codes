'''MIR-02 IT III'''

bal = 500

while  True:
    print("---ATM MENU---")
    print("1. Balance Inquiry")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Exit")

    choose = input("Choose your move (1-4): ")

    if choose == "1":
        print(f"Your current balance is ₱: {bal:.2f}")
    elif choose == "2":
        amount = float(input("Enter Deposit Amount: ₱ "))
        if amount <= 0:
            print("Invalid! Please try again.")
        else:
            bal += amount
            print(f"Success! Your new balance is: ₱ {bal:.2f}")
    
    elif choose == "3":
        amount = float(input("Enter Withdrawal Amount: ₱ "))
        if amount <= 0:
            print("Invalid! Please try again")
        elif amount > bal:
            print("Insufficient Funds. Withdrawal Denied.")
        else:
            bal -= amount
            print(f"Success! Remaining Balance : ₱ {bal:.2f}")

    elif choose == "4":
        print("Thank you! Please come again! ")
        break