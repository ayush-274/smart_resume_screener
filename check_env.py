# check_env.py
import sys
import os

print("--- Environment Check ---")
print(f"Python Executable: {sys.executable}")
print(f"Virtual Environment: {os.getenv('VIRTUAL_ENV')}")
print("-----------------------")