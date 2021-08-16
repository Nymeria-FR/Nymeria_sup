import sys
import os
import signal

from config import TomlConfig

config = TomlConfig("config.toml", "config.template.toml")
values = sys.argv[1:]

if values[0] == "start":
    for key in config.bots.keys():
        if len(values[1:]) == 0 or key in values:
            print("Lancemnet : " + key)
            os.system("python3 nymeria_sup.py " + key + "&")

elif values[0] == "stop":
    with open(config.extern["pid"], "r") as folder:
        pids = folder.read()
        pids_array = pids.split("\n")
        pid_it = 0
        for pid in pids_array:
            if len(values) < 2 or pid.split(" ")[0] in values[1:]:
                print("kill : " + pid)
                os.kill(int(pids_array[0].split(" ")[1]), signal.SIGINT)
                del pids_array[pid_it]
            pid_it += 1
        pid_str = "\n".join(pids_array)

    with open(config.extern["pid"], "w") as folder:
        folder.write(pid_str)
