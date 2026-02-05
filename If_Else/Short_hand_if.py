#Short Hand If


#If you have only one statement to execute, you can put it on the same line as the if statement.
a = 1000
b = 999
if a > b: print("a is greater than b")

#Short Hand If-Else
a = 2
b = 330
print("A") if a > b else print("B")

#one-line if/else to choose a value and assign it to a variable:
a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

#One line, three outcomes:

a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")