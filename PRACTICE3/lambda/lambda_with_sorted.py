# Using lambda functions with sorted()
students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])
print(sorted_students)


# Second example
favorite_numbers = [5, 2, 9, 1, 5, 13]
sorted_numbers = sorted(favorite_numbers, key=lambda x: x)
print(sorted_numbers)


# Third example
jobs = [("Software Engineer", 70000), ("Data Scientist", 90000), ("Product Manager", 80000)]
priotized_jobs = sorted(jobs, key=lambda x: x[-1])
print(priotized_jobs)


# Fourth example
cars = [("Toyota", 2020), ("Honda", 2018), ("Ford", 2021)]
oldest_to_newest = sorted(cars, key=lambda x: x[1])
print(oldest_to_newest)