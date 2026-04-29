day = 4
days = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday"
    }
print(days.get(day, "Invalid day"))


battery_level = 30
print("Battery level is high" if battery_level >= 80 else 
      "Battery level is medium" if battery_level >= 30 else "Battery level is low")



password = False
result = "Access granted" if password else "Access denied"
print(result)


number = 10
print("The number is even") if number % 2 == 0 else print("The number is odd")


score = 95
print("Grade: A" if score >= 90 else
      "Grade: B" if score >= 80 else
      "Grade: C" if score >= 70 else
      "Grade: D" if score >= 60 else
      "Grade: F")