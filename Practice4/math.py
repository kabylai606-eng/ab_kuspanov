import math

# 1) Degree -> Radian
deg = 15
rad = deg * (math.pi / 180)
print(format(rad))


# 2) Area of a trapezoid: A = (a + b) / 2 * h
h = 5
a = 5
b = 6
trap_area = (a + b) / 2 * h
print(trap_area)


# 3) Area of a regular polygon: A = (n * s^2) / (4 * tan(pi/n))
n = 4
s = 25
poly_area = (n * (s ** 2)) / (4 * math.tan(math.pi / n))
print(poly_area)


# 4) Area of a parallelogram: A = base * height
base = 5
height = 6
para_area = base * height
print(float(para_area))