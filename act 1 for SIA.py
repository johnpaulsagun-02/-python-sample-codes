current_time = int(input("Current Time (0:23): "))
current_minute = int(input("Current time in minute (0:59): "))
trip_time = int(input("Trip time in minutes: "))

total_minutes = (trip_time * 60) + current_minute

arrival_total = total_minutes + trip_time

arrival_time = (arrival_total // 60) % 24
arrival_minute = arrival_total % 60

print(f"\nArrival hour: {arrival_time} | Arrival minute: {arrival_minute}")