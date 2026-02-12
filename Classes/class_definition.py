#Create a Class
#To create a class, use the keyword class:

#Create a class named MyClass, with a property named x:

class MyClass:
  x = 5
  
  
#Create a Class with name and ages of students
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print("Hi, my name is", self.name, "and I am", self.age, "years old.")
