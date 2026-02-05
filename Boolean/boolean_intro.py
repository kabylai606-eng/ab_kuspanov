#Boolean Values
print(10 > 9)
print(10 == 9)
print(10 < 9)


#Print a message based on whether the condition is True or False.
a = 1000
b = 999

if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")
  
#The bool() function allows you to evaluate any value, and give you True or False in return
print(bool("Hello, Abylai!"))
print(bool(20))

#Another example
x = "Hello, Abylai!"
y = 20

print(bool(x))
print(bool(y))

#Almost any value is evaluated to True if it has some sort of content
bool("abc")
bool(123)
bool(["apple", "cherry", "banana"])


#Some values are False
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})

