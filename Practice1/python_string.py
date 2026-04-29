#length of the string------------------------------------------------------------------------------------------------------------------------------
a = "Hello, World!"
print(len(a))   

#checking in the string-----------------------------------------------------------------------------------------------------------------
txt = "The best things in life are free!"
print("free" in txt)

#Slicing--------------------------------------------------------------------------------------------------------------------------
b = "Hello, World!"
print(b[2:5]) #from 2, to 4(include)

b = "Hello, World!"
print(b[:5]) #from the start to 4(included)

b = "Hello, World!"
print(b[2:])#from 2 to the end

b = "Hello, World!"
print(b[-5:-2]) #from index -5 to -3

#Modifying-------------------------------------------------------------------------------------------------------------------------------
a = "Hello, World!"
print(a.upper())#in the upper case HELLO WORLD

a = "Hello, World!"
print(a.lower())#in the lower case hello world

a = " Hello, World! "
print(a.strip()) # returns "Hello, World!"

a = "Hello, World!"
print(a.replace("H", "J")) #Jello, World!

a = "Hello, World!"
print(a.split(",")) # returns ['Hello', ' World!']

#Concatenation--------------------------------------------------------------------------------------------------------------------------
a = "Hello"
b = "World"
c = a + b
print(c) 

#Format string----------------------------------------------------------------------------------------------------------------------
age = 19
txt = f"My name is Yernar, I am {age}"
print(txt)

price = 59
txt = f"The price is {price} dollars"
print(txt)


price = 59
txt = f"The price is {price:.2f} dollars"
print(txt)


txt = f"The price is {20 * 10} dollars"
print(txt)