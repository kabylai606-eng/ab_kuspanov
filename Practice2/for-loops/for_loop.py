# Example 1
fruits = ["PP2", "CALC2", "PHYSICS2"]
for x in fruits:
  print("Todays classes :", x)
  
# Example 2
i = 10
for i in range(10):
    print(i)
print("Test is ended !")

# Example 3
age = 7
for age in range(7, 18):
    print(f"You are {age} years old. You are not adult yet.")
print("You are now an adult!")
        
# Example 4    
money = 0
cost_of_item = 1000
for i in range(cost_of_item // 100):
    print(f"{cost_of_item - money} $ left to buy the item.")
    money += 100 
print("You have enough money to buy the item!")
    
# Example 5
level = 1
for level in range(1, 10):
    print(f"Level {level} — keep learning and grinding !")
print("Congratulations! You have reached the final level!")