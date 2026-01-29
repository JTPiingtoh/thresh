options = {"A": 1, "B": 2, "C": 3}
more_options = [
    {"A": 1, "B": 2, "C": 3},
    {"A": 4, "B": 5, "C": 6},
]


for opt in more_options:
    print(opt["B"])