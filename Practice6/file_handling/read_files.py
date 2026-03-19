#We have txt file
#Hello! Welcome to demofile.txt
#This file is for testing purposes.
#Good Luck!


#To open the file, use the built-in open() function.

#The open() function returns a file object, which has a read() method for reading the content of the file:

f = open("demofile.txt")
print(f.read())


#You can also use the with statement when opening a file:
with open("demofile.txt") as f:
  print(f.read())
  
  
#CLOSE FILES
#Close the file when you are finished with it:

f = open("demofile.txt")
print(f.readline())
f.close()

#Read Only Parts of the File
with open("demofile.txt") as f:
  print(f.read(5))
  
  
#READ FILES
#You can return one line by using the readline() method:
with open("demofile.txt") as f:
  print(f.readline())


#By calling readline() two times, you can read the two first lines:
with open("demofile.txt") as f:
  print(f.readline())
  print(f.readline())
  
#By looping through the lines of the file, you can read the whole file, line by line:
with open("demofile.txt") as f:
  for x in f:
    print(x)