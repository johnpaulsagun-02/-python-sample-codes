print("Quadratic Equation")

for x in range (1, 7):
  a = float(input("a : "))
  b = float(input("b : "))
  c = float(input("c : "))

  d = (b ** 2 - 4 * a * c) ** 0.5
  x1 = (-b + d) / ( 2 * a)
  x2 = (-b - d) / (2 * a)

  print(f"Output :  {x1}, {x2}\n")