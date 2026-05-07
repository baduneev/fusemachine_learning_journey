import os

from dotenv import load_dotenv, dotenv_values


load_dotenv()  # Load environment variables from .env file  

print("MY_SECRET_KEY:", os.getenv("MY_SECRET_KEY"))  # Access using os.getenv
print("COMBINED:", os.getenv("COMBINED"))  # Access using os.getenv


config = dotenv_values(".env")  # Load .env file into a dictionary
print(config)  # Print the loaded configuration as a dictionary

