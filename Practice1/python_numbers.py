#int
#float
#complex

x = 1
y = 99999999
z = -9999999

print(type(x))
print(type(y))
print(type(z))

x = 1.10
y = 1.0
z = -35.59

print(type(x))
print(type(y))
print(type(z))

x = 3+5j
y = 5j
z = -5j

print(type(x))
print(type(y))
print(type(z))


x = 1    # int
y = 9.9  # float
z = 5j   # complex

#convert from int to float:
a = float(x)

#convert from float to int:
b = int(y)

#convert from int to complex:
c = complex(x)

print(a)
print(b)
print(c)

print(type(a))
print(type(b))
print(type(c))



#random 
import random

print(random.randrange(1, 10))