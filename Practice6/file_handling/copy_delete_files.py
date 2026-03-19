#DELETE A FILE
#To delete a file, you must import the OS module, and run its os.remove() function:
#Remove the file "demofile.txt":

import os
import shutil
os.remove("demofile.txt")
# Copy the file "demofile.txt"
shutil.copy("demofile.txt", "copy.txt")



#CHECK IF FILE EXIST
#Check if file exists, then delete it:

import os
if os.path.exists("demofile.txt"):
  os.remove("demofile.txt")
else:
  print("The file does not exist")
  
#DELETE FOLDER
#To delete an entire folder, use the os.rmdir() method:
#Remove the folder "myfolder":

import os
os.rmdir("myfolder")

