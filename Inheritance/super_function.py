#Python also has a super() function that will make the child class inherit all the methods and properties from its parent:

class Student():
  def __init__(self, fname, lname):
    super().__init__(fname, lname) 
    
#Add a property called graduationyear to the Student class:
class Student():
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

x = Student("Mike", "Olsen", 2019)


#Add a year parameter, and pass the correct year when creating objects:
class Student():
  def __init__(self, fname, lname):
    super().__init__(fname, lname)
    self.graduationyear = 2019


#Add a method called welcome to the Student class:

class Student():
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear)
    

#Add a method called welcome to the Student class:

class Student():
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear)
