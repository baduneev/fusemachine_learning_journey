"""One command for the required Track A workflow."""
from src.train import main as train
from src.monitor import main as monitor

if __name__ == "__main__":
    train()
    monitor()
