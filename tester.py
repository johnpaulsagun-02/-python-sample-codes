SENTINEL = -2
MIN   = 1
MAX =  999
 


def get_numbers():
    
    numbers = []
    print(f"Enter numbers between {MIN} and {MAX}.")
    print(f"Enter {SENTINEL} when you are finished.\n")
 
    while True:
        value = int(input("Enter a number: "))
        if value == SENTINEL:
            break
        if value < MIN or value > MAX:
            print(f"  Please enter a number between {MIN} and {MAX}.")
            continue
        numbers.append(value)
 
    return numbers
 
 
def get_average(numbers):
    return sum(numbers) / len(numbers)
 
 
def get_maximum(numbers):
    return max(numbers)
 
 
def get_minimum(numbers):
    return min(numbers)
 
 
def get_range(numbers):
    return get_maximum(numbers) - get_minimum(numbers)
 
 
def get_mode(numbers):
    counts = {}
    for n in numbers:
        counts[n] = counts.get(n, 0) + 1
 
    best_number = numbers[0]
    best_count = 0
    for number, count in counts.items():
        if count > best_count:
            best_count = count
            best_number = number
 
    return best_number
 
 
def print_histogram(numbers):
    print("\nHistogram")
    for low in range(1, MAX, 5):
        high = low + 4
        count = 0
        for n in numbers:
            if low <= n <= high:
                count += 1
        stars = "*" * count
        print(f"{low:>2} - {high:<2}: {stars}")
 
 
def main():
    numbers = get_numbers()
 
    if not numbers:
        print("No numbers were entered.")
        return
 
    print("\n--- Analysis ---")
    print(f"Average: {get_average(numbers):.2f}")
    print(f"Maximum: {get_maximum(numbers)}")
    print(f"Minimum: {get_minimum(numbers)}")
    print(f"Range:   {get_range(numbers)}")
    print(f"Mode:    {get_mode(numbers)}")
 
    print_histogram(numbers)
 
 
if __name__ == "__main__":
    main()
 