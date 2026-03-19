from functools import reduce

nums = [1, 2, 3, 4]

# map
squares = list(map(lambda x: x**2, nums))
print(squares)

# filter
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)

# reduce
product = reduce(lambda a, b: a * b, nums)
print(product)