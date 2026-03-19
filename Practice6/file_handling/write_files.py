#WRITE TO AN EXICTING FILE
#To write to an existing file, you must add a parameter to the open() function:

#"a" - Append - will append to the end of the file

#"w" - Write - will overwrite any existing content


#Open the file "demofile.txt" and append content to the file:

with open("demofile.txt", "a") as f:
  f.write("Now the file has more content!")

#open and read the file after the appending:
with open("demofile.txt") as f:
  print(f.read())
  
  
  
#OVERWRITE EXISTING CONTENT
#To overwrite the existing content to the file, use the w parameter:
#Open the file "demofile.txt" and overwrite the content:

with open("demofile.txt", "w") as f:
  f.write("Woops! I have deleted the content!")

#open and read the file after the overwriting:
with open("demofile.txt") as f:
  print(f.read())
  
  
  
#CREATE A NEW FILE
#To create a new file in Python, use the open() method, with one of the following parameters:

#"x" - Create - will create a file, returns an error if the file exists

#Create a new file called "myfile.txt":

f = open("myfile.txt", "x")

