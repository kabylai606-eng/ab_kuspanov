names = ["A", "B", "C"]
scores = [10, 20, 30]

# enumerate
for i, name in enumerate(names):
    print(i, name)

# zip
for name, score in zip(names, scores):
    print(name, score)