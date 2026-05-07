import argparse

parser = argparse.ArgumentParser()

parser.add_argument("numbers", type=int, nargs="+")

args = parser.parse_args()

print("Numbers:", args.numbers)
print("Sum:", sum(args.numbers))