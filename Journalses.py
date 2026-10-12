"""Coder: Hee hee
           JP MIR 
               hee hee aay"""

from datetime import datetime

class Diary:

    def __init__(self, filename="journal.txt"):
        self.filename = filename

    def menu(self):
        print("=" * 25 + "\n" + "DAILY JOURNAL & DIARY LOGGER" + "\n" + "=" * 25)
        print("1. Write New Journal Entry")
        print("2. View All Journal Entries")
        print("3. Exit")

    def write(self):
        print("\n" + "-" * 5 + "Write New Entry" + "-" * 5)
        entries = input("Enter your thoughts for today:" + "\n>")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.filename, "a") as file:
            file.write("=" * 40 + "\n")
            file.write(f"Date/Time: {timestamp}\n")
            file.write("Entry:\n")
            file.write(f"{entries}\n")
            file.write("=" * 40 + "\n\n")

        print("☑️ Journal entry saved successfully!\n")

    def view_journal(self):
        print("\n" + "-" * 5 + "Past Journal Entries" + "-" * 5)
        try:
            with open(self.filename, "r") as file:
                lines = file.readlines()
                if len(lines) == 0:
                    print("Oops... There's no journal entries yet.\n")
                else:
                    for line in lines:
                        print(line.rstrip())
                    print()
        except FileNotFoundError:
            print("No journal entries yet. Maybe, write one first.\n")

logbook = Diary()

while True:
    logbook.menu()
    choice = input("Select an option (1-3): ")

    if choice == "1":
        logbook.write()
    elif choice == "2":
        logbook.view_journal()
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice! Select 1, 2 and 3 only.\n")