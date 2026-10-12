""" CODEr
           JOHN PAUL MIR
            BSIT III
               HEE HEE ~"""



prices = [3, 4, 2]


sales = [
    [13, 9, 7, 15],   
    [8, 7, 4, 6],     
    [6, 4, 0, 3]      
]

days = ["Mon", "Tue", "Wed", "Thu"]
pie_types = ["Bayabas", "Rambutan", "Suha"]


print("Breakdown per day:")
for day_index in range(len(days)):
    parts = []
    day_total = 0
    for pie_index in range(len(prices)):
        value = prices[pie_index] * sales[pie_index][day_index]
        parts.append(f"${prices[pie_index]}x{sales[pie_index][day_index]}={value}")
        day_total += value
    print(f"{days[day_index]}: " + " + ".join(parts) + f" = ${day_total}")

print()


print("Matrix form:")
print(f"[{' '.join('$'+str(p) for p in prices)}] x [")
for row in sales:
    print("  " + " ".join(str(v) for v in row))
print("] =")

totals = []
for day_index in range(len(days)):
    day_total = sum(prices[i] * sales[i][day_index] for i in range(len(prices)))
    totals.append(day_total)

print("[" + " ".join(f"${t}" for t in totals) + "]")