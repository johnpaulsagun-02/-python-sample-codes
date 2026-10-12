print("numbers desicion (kape)")

def number_to_words(n):
    ones = ["zero","one","two","three","four","five","six","seven","eight","nine",
            "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
            "seventeen","eighteen","nineteen"]
    tens = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]

    if n == 0:
        return "Zero"

    h, r = n // 100, n % 100
    words = ""

    if h > 0:
        words += ones[h] + " hundred"
        if r > 0:
            words += " and " if r < 10 else " "

    if r >= 20:
        words += tens[r // 10] + (" " + ones[r % 10] if r % 10 else "")
    elif r > 0:
        words += ones[r]

    return words.capitalize()


n = int(input("Enter a number (0-999): "))

if n < 0 or n > 999:
    print("Number must be between 0 and 999")
else:
    print(f"{n} --> \"{number_to_words(n)}\"")