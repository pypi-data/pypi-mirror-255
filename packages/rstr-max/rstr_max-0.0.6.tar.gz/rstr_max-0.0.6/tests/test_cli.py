import sys

from src.rstr_max.cli import *

sys.argv = ["rstr_max", "-i", "lorem.txt", "-o", "lorem.json", "-v"]
print(f"Run 1: {sys.argv = }")
main()
# with open("lorem.json", "r") as f:
#     print(f.read())

sys.argv = ["rstr_max", "-i", "lorem.txt", "-o", "lorem.json", "-v", "-M", "4", "-m", "2"]
print(f"\n\nRun 2: {sys.argv = }")
main()
# with open("lorem.json", "r") as f:
#     print(f.read())

sys.argv = ["rstr_max", "--version"]
print(f"\n\nRun 3: {sys.argv = }")
main()

