class Student:
    school = "KBTU"

    def __init__(self, name):
        self.name = name

s1 = Student("Aida")
s2 = Student("Sanzhar")

print(s1.school)
print(s2.school)