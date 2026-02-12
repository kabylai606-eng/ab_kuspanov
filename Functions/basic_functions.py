#Creating a function
#A function is defined using the def keyword

def my_function():
  print("Hello from a function")
  
#To call a function, write its name followed by parentheses:
def my_function():
  print("Hello from a function")

my_function()

#You can call the same function multiple times:
def my_function():
  print("Hello from a function")

my_function()
my_function()
my_function()


#Why Use Functions?
#Without functions - repetitive code:
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)

#With function reusable code:
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))

#A function that returns a value:
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)


#The Pass Statement:
def my_function():
  pass