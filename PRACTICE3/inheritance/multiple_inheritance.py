class Father:
    def skill(self):
        print("Programming")

class Mother:
    def talent(self):
        print("Design")

class Child(Father, Mother):
    pass

c = Child()
c.skill()
c.talent()