import sys
import os

value = sys.argv[1:]

if value[0] == "start":
    if len(value[1:]) == 0:
        print(os.system("python3 nymeria_sup.py staf &"))
elif value[0] == "stop":
    if len(value[1:]) == 0:
        print(os.system("python3 nymeria_sup.py staf &"))