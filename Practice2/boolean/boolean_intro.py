#We could use bool() function to evaluate any value, and give you True or False in retur
print(1 == 1)
print(1 < 1)
print(1 > 1)
print(1 >= 1)
print(1 <= 1)


print("-----") 

  
first = 2
second = 1
if first > second:
  print("first number is greater than second")
else:
  print("first is not greater than second")
  
first = 1
second = 2
if first > second:
  print("first number is greater than second")
else:
  print("first is not greater than second")

first = 3
second = 3
if first > second:
    print("first number is greater than second")
elif first == second:
    print("first is equal to second")
else:
    print("first is not greater than second")


print("-----")


#The bool() function allows you to evaluate any value, and give you True or False in return,


print(bool("any integer will be True except 0")) #Any integer except 0 is True
print(bool(777)) # Any integer is True
print(bool(0)) # Except 0 is False
print(bool(-1)) # negative numbers is True
print(bool(0.1)) # Float is True
print(bool("")) # Empty string is False
print(bool()) # Empty value is False
bool(()) # Empty tuple is False
bool([]) # Empty list is False
bool({}) # Empty dictionary is False
bool(False) # False is False
bool(None) # None is False


print("-----") 


# Functions can Return a Boolean Value
def FunctionOfYernar() :
  return True
print(FunctionOfYernar())

def FunctionOfYernar() :
  return False
print(FunctionOfYernar())


def myFunction() :
  return True

if myFunction():
  print("The value is True")
else:
  print("The value is False")

def myFunction() :
  return False

if myFunction():
  print("The value is True")
else:
  print("The value is False")


print("-----")


x = 999
print(isinstance(x, int)) # Returns True because x is an integer

y = "Yernar"
print(isinstance(y, str)) # Returns True because y is a string


print("-----")