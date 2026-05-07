import argparse

parser = argparse.ArgumentParser(description="A simple argument parser example")

parser.add_argument(
    "--mode",
    choices=["train", "test", "predict"],
    default="train"
)

args = parser.parse_args()

print("Mode:", args.mode)