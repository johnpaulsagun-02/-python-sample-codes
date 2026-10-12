""" Code
        by
            JPaul Mir 
                Hee Hee~"""


TAX_RATE = 0.08  
 
cart_items = []   
cart_prices = []  
 
 
def add_item():
    name = input("Enter item name: ").strip()
    if not name:
        print("Item name cannot be empty.\n")
        return
 
    while True:
        price_input = input(f"Enter price for '{name}': $").strip()
        try:
            price = float(price_input)
            if price < 0:
                print("Price cannot be negative. Try again.")
                continue
            break
        except ValueError:
            print("Invalid price. Please enter a number (e.g. 9.99).")
 
    cart_items.append(name)
    cart_prices.append(price)
    print(f"Added '{name}' - ${price:.2f}\n")
 
 
def remove_item():
    if not cart_items:
        print("Cart is empty. Nothing to remove.\n")
        return
 
    print("\nCurrent items:")
    for i, (name, price) in enumerate(zip(cart_items, cart_prices), start=1):
        print(f"  {i}. {name} - ${price:.2f}")
 
    choice = input("\nEnter the number of the item to remove (or 'c' to cancel): ").strip()
    if choice.lower() == 'c':
        print("Cancelled.\n")
        return
 
    try:
        index = int(choice) - 1
        if 0 <= index < len(cart_items):
            removed_name = cart_items.pop(index)
            removed_price = cart_prices.pop(index)
            print(f"Removed '{removed_name}' - ${removed_price:.2f}\n")
        else:
            print("Invalid item number.\n")
    except ValueError:
        print("Invalid input.\n")
 
 
def view_cart():
    if not cart_items:
        print("Your cart is empty.\n")
        return
 
    subtotal = sum(cart_prices)
    tax = subtotal * TAX_RATE
    total = subtotal + tax
 
    print("\n" + "=" * 40)
    print(f"{'YOUR CART':^40}")
    print("=" * 40)
    print(f"{'Item':<25}{'Price':>15}")
    print("-" * 40)
    for name, price in zip(cart_items, cart_prices):
        print(f"{name:<25}{'$' + f'{price:.2f}':>15}")
    print("-" * 40)
    print(f"{'Subtotal:':<25}{'$' + f'{subtotal:.2f}':>15}")
    print(f"{'Tax (' + f'{TAX_RATE * 100:.0f}%):':<25}{'$' + f'{tax:.2f}':>15}")
    print(f"{'Total:':<25}{'$' + f'{total:.2f}':>15}")
    print("=" * 40 + "\n")
 
 
def print_menu():
    print("=" * 30)
    print("     SHOPPING CART MENU")
    print("=" * 30)
    print("1. Add item")
    print("2. Remove item")
    print("3. View cart")
    print("4. Exit")
 
 
def main():
    print("Welcome to the CLI Shopping Cart!\n")
    while True:
        print_menu()
        choice = input("Choose an option (1-4): ").strip()
 
        if choice == '1':
            add_item()
        elif choice == '2':
            remove_item()
        elif choice == '3':
            view_cart()
        elif choice == '4':
            print("Thanks for shopping! Goodbye.")
            break
        else:
            print("Invalid choice. Please select 1-4.\n")
 
 
if __name__ == "__main__":
    main()