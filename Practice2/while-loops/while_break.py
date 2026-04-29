# Example 1
while True:
    password = input("Enter the password: ")
    if password == "secret":
        print("Access granted!")
        break
    else:
        print("Wrong password, try again.")
        
       
# Example 2
secret = 13
while True:
    guess = int(input("Guess the secret number (between 1 and 20): "))
    if guess == secret:
        print("Correct! You guessed it.")
        break
    else:
        print("Try again.")

    
# Example 3
i = 0
while True:
    print("Attempt", i)
    i += 1
    if i == 3:  
        print("Reached 3 attempts, exiting.")
        break


# Example 4
names = ["Alice", "Bob", "Charlie", "David", "Trump", "Eve"]
i = 0
while i < len(names):
    if names[i] == "Trump":
        print("President of USA : ", names[i])
        break
    i += 1

    
# Example 5
ytubes = ["Music", "Education", "Comedy", "News", "Sports", "Movies"]
i = 0
while i < len(ytubes):
    if ytubes[i] == "Comedy":
        print("Today I will watch", ytubes[i])
        break
    i += 1