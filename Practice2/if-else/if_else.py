Friends = ["Yernur", "Azamat", "Sultan", "Nurkohza"]
if (count := len(Friends)) > 0:
    print(f"Yernar has {count} friends")
else :
    print("Yernar has no friends")
    
    
    
password = False
if password:
  print("Access granted")
else:
  print("Access denied")
  
  

points = 75
if points >= 50:
  print("Congratulations! You passed the exam.")
else:
  print("Sorry, you did not pass the exam.")
  
  
  
age = 18
if age < 18:
  pass # TODO: Add underage logic later
else:
    print("You are an adult.")
    
    
number = 10
if number % 2 == 0: print("The number is even")
else: print("The number is odd")