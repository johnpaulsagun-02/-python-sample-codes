"""Coded by: the BOI
            JP MIR
                 Kape ''"""

import array as ah

ah = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
]

print("Original Arry:")
for l in range(0, 3):
    for p in range(0, 4):
        print(ah[l][p], end= " ")
    print()

ahh = []

for l in range(0,4):
    row = []
    for p in range (0, 3):
        row.append (ah[p][l])
    ahh.append(row)

print("\n Transformer Arry: ")
for l in range(0, 4):
    for p in range(0, 3):
        print(ahh[l][p], end= " ")
    print()