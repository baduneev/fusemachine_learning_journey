import argparse

parser = argparse.ArgumentParser(description="A simple argument parser example")

# parser.add_argument("name")  # for optional argument, use --name
# parser.add_argument("age", type=int)

# args = parser.parse_args()

# print("Name:", args.name)
# print("Age:", args.age)


# parser.add_argument("num1", type=int) 
# parser.add_argument("num2", type=int)
# args = parser.parse_args()

# print("Difference:", args.num1 - args.num2)

parser.add_argument("--name", default = 'Neev', help = "Enter your name")  # for optional argument, use --name
parser.add_argument("--age", type=int, default = 22, help = "Enter your age")  # for optional argument, use --age

args = parser.parse_args()

print("Name:", args.name)
print("Age:", args.age)
