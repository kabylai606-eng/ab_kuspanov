#A function that returns a value:
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)

#Return Values
def my_function(x, y):
  return x + y

result = my_function(5, 3)
print(result)


#Returning Different Data Types
def my_function():
  return ["apple", "banana", "cherry"]

fruits = my_function()
print(fruits[0])
print(fruits[1])
print(fruits[2])
