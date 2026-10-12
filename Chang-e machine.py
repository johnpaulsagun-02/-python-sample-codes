print("#" * 75)
print(" Change Machine ")
print("#" * 75)

dollar = 0
quarts = 0
dimes = 0
nickel = 0
penny = 0

cash_pay = float(input("Amount of Payment :  "))
total_pay = float(input(" Total payment: "))

change = round((cash_pay - total_pay) * 100)


print(f"\n Change Due : $ {change / 100:.2f}\n")

dollar = change // 100
change = change % 100

quarts = change // 25
change = change % 25

dimes = change // 10
change = change % 10

nickel = change // 5
change = change % 5

penny = change // 1
change = change % 1

print(" Change Due: ")
print(" Dollar: ", dollar)
print(" Quarts: ", quarts)
print(" Dimes: ", dimes)
print(" Nickels: ", nickel)
print(" Pennies: ", penny)