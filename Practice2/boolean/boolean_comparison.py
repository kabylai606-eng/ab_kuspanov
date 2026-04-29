#Comparison Operators

a = 5
b = 10
print(a == b)
print(a != b)
print(a > b)
print(a < b)
print(a >= b)
print(a <= b)
print(not(a < b))
print((a < b) and (a != b))
print((a < b) or (a == b))

a = 7
b = 13
print(a > b)

x = 9
y = 15
print(x > y)


e = 7
u = 13
print(e <= u)

w = 12
q= 87
print(w <= q)


#Arithmetic Operators
x = 10
y = 10

print(x + y) # + - Addition
print(x - y) # - Subtraction
print(x * y) # * - Multiplication
print(x / y) # / - Division (returns a float)
print(x % y) # % - Modulus (returns the remainder)
print(x ** y)  # ** - Exponentiation (x raised to the power of y)
print(x // y)  # // - Floor Division (returns the largest integer less than or equal to the division result)


#Assignment Operators

x = 10
x += 10
print(x)  # Output: 20
x -= 5
print(x)  # Output: 5
x *= 10
print(x)  # Output: 50
x /= 10
print(x)  # Output: 5.0
x %= 5
print(x)  # Output: 0.0


#Comparison Operators


a = 5
b = 10
print(a == b)
print(a != b)
print(a > b)
print(a < b)
print(a >= b)
print(a <= b)
print(not(a < b))
print((a < b) and (a != b))
print((a < b) or (a == b))


#Logical Operators


E = 1
print(E > 1 and E < 5)
R = 2
print(R > 2 and R < 4)
N = 3
print(N > 3 and N < 3)
A = 4
print(A > 4 and A < 2)
R = 5
print(R > 5 and R < 1)


#Identity Operators


x = ["Windows", "Samsung"]
y = ["MacBook", "Iphone"]
print(x is not y)

x = ["Monday", "Friday"]
y = ["Saturday", "Sunday"]
print(x is y)

x = [13, 14, 15]
y = [13, 14, 15]
print(x == y)


#Membership Operators    


Phones = ["Samsung", "Apple", "Huawei"]

print("Samsung" in Phones)
print("Xiaomi" not in Phones)


text = "I am student of KBTU"

print("K" in text)
print("hello" in text)
print("Yernar" not in text)