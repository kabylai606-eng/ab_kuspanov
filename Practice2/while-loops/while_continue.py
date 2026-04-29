# Example 1
list_of_friends = ["Yernar", "Nurik", "Dastan", "Asylzat", "Aibek"]
i = 0
while i < len(list_of_friends):
    if list_of_friends[i] == "Yernar":
        i += 1
        continue
    print("This person isn't my bestfriend:", list_of_friends[i])
    i += 1


# Example 2
brands_of_phone = ["Samsung", "Iphone", "Xiaomi", "Oppo", "Vivo", "Realme"]
i = 0
while i < len(brands_of_phone):
    if brands_of_phone[i] == "Iphone":
        i += 1
        continue
    print("I do not use:", brands_of_phone[i])
    i += 1
    
    
# Example 3
ytubes = ["Music", "Education", "Comedy", "News", "Sports", "Movies"]
i = 0
while i < len(ytubes):
    if ytubes[i] == "Movies":
        i += 1
        continue
    print("I do not watch:", ytubes[i])
    i += 1


# Example 4
names = ["Alice", "Bob", "Charlie", "David", "Trump", "Eve"]
i = 0
while i < len(names):
    if names[i] == "Trump":
        i += 1
        continue
    print("This person is not a President:", names[i])
    i += 1


# Example 5
i = 0
while i < 6:
  i += 1
  if i == 3:
    continue
  print(i)