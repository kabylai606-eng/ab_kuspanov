#Python Inheritance
#Create a class named Person, with firstname and lastname properties, and a printname method:

class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the printname method:

x = Person("John", "Doe")
x.printname()



#Add the __init__() Function
#Add the __init__() function to the Student class:

class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)
    
    
    
class Animal:
    def speak(self):
        print("Animal makes a sound")

class Dog(Animal):
    pass

d = Dog()
d.speak()