import os

def walk_directory(path):
    for root, dirs, files in os.walk(path):
        print(f"Directory: {root}")
        for file in files:
            print(f"  File: {file}")
        for dir in dirs:
            print(f"  Subdirectory: {dir}")


# Example usage:
walk_directory("./code_gen")