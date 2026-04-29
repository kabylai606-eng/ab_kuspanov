#Python Variables-------------------------------------------------------------------------------------------------------------------
x = 19       #int
y = "Yernar" #str

print("Age:", x)
print("Name:", y)

x = 19       # x is of type int
x = "Yernar" # x is now of type str
print(x)     # and result will be the last value of x

#by the command type we can understand what type 
x = 19     
y = "Yernar"
print(type(x))
print(type(y))

y = "Yernar" 
#is the same as 
y = 'Yernar'

a = 19
A = "Yernar"
print (a, A)
# a & A is the 2 different variables now


#Variable Names-------------------------------------------------------------------------------------------------------------------

myvar = "Yernar"
my_var = "Yernar"
_my_var = "Yernar"
myVar = "Yernar"
MYVAR = "Yernar"
myvar2 = "Yernar"



#2myvar = "Yernar"
#my-var = "Yernar"
#my var = "Yernar"
#examples of inccorrect variable names
#Remember that variable names are case-sensitive  


#Assign Multiple Values------------------------------------------------------------------------------------------------------------------- 
x, y, z = "Sultan", "Bogdan", "Jalgas"
print(x)
print(y)
print(z)


friends = ["Sultan", "Bogdan", "Jalgas"] 
first, second, third = friends
print(first, second, third)


#Output Variables------------------------------------------------------------------------------------------------------------------- 

#Don't forget about comma after variables
x = "Today"
y = " I have"
z = " a class"
print(x, y, z)
#You can also use the + operator to output multiple variables:
x = "Today"
y = " I have"
z = " a class"
print(x + y + z)

#also + works as a mathematical operator
x = 5 
y = 5 
print(x + y)

#Remember when u combine str and number it will be error instead use comma
x = 19     
y = "Yernar"
print(x,y)


#Global Variables------------------------------------------------------------------------------------------------------------------- 

x = "easy to understand"
def myfunc():
  print("Python is " + x)

myfunc() 


x = "easy to understand"
def myfunc():
  x = "hard for me"
  print("Python is " + x)

myfunc()

print("Python is " + x)

#the function global changes the variable 

x = "hard"

def myfunc():
  global x
  x = "easy"

myfunc()

print("Python is " + x)