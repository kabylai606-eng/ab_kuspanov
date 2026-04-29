# 1) Squares up to N

def squares_up_to(n):
    for i in range(1, n + 1):
        yield i * i

print(list(squares_up_to(5)))  


# 2) Even numbers 0..n (comma-separated)

def even_numbers(n):
    for i in range(0, n + 1, 2):
        yield i

print(",".join(str(x) for x in even_numbers(20)))


# 3) Divisible by 3 and 4 (0..n)

def divisible_by_3_and_4(n):
    for x in range(0, n + 1):
        if x % 3 == 0 and x % 4 == 0:
            yield x

print(" ".join(str(x) for x in divisible_by_3_and_4(50)))


# 4) squares(a, b)

def squares(a, b):
    for x in range(a, b + 1):
        yield x * x

for val in squares(3, 7):
    print(val)



# 5) Countdown n..0

def countdown(n):
    for x in range(n, -1, -1):
        yield x

for x in countdown(5):
    print(x)