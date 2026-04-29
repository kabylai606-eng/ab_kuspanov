# Example 1
list_of_friends = ["Yernar", "Nurik", "Dastan", "Asylzat", "Aibek"]
i = 0
for i in range(len(list_of_friends)):
    if list_of_friends[i] == "Yernar":
        continue
    print("This person isn't my bestfriend:", list_of_friends[i])

# Example 2
    
brands_of_phone = ["Samsung", "Iphone", "Xiaomi", "Oppo", "Vivo", "Realme"]
i = 0
for i in range(len(brands_of_phone)):
    if brands_of_phone[i] == "Iphone":
        continue
    print("I do not use:", brands_of_phone[i])
 
# Example 3

ytubes = ["Music", "Education", "Comedy", "News", "Sports", "Movies"]
i = 0
for i in range(len(ytubes)):
    if ytubes[i] == "Movies":
        i += 1
        continue
    print("I do not watch:", ytubes[i])

# Example 4

names = ["Alice", "Bob", "Charlie", "David", "Trump", "Eve"]
i = 0
for i in range(len(names)):
    if names[i] == "Trump":
        continue
    print("This person is not a President:", names[i])

# Example 5
    
i = 0 
for i in range(6):
  if i == 3:
    continue
  print(i)