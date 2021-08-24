import sys
import os
import signal

from config import TomlConfig

config = TomlConfig("config.toml", "config.template.toml")
values = sys.argv[1:]

if values[0] == "start":
    with open(config.extern["pid"], "r") as folder:
        pids = folder.read()
        pids = pids.split("\n")
        names = [pid.split(" ")[0] for pid in pids]
        if len(values[1:]) == 0:
            for name in config.bots.keys():
                if not name in names:
                    values.append(name)
        for key in config.bots.keys():
            if key in values:
                print("Lancemnet : " + key)
                os.system("python3 nymeria_sup.py " + key + "&")

elif values[0] == "stop":
    with open(config.extern["pid"], "r") as folder:
        pids = folder.read()
        pids_array = pids.split("\n")
        pid_max = len(pids_array)
        pid = 0
        while pid < len(pids_array) - 1:
            array = pids_array[pid].split(" ")
            if (len(values) < 2 or array[0] in values[1:]) and len(array) == 2:
                print("kill : " + pids_array[pid])
                os.kill(int(array[1]), signal.SIGINT)
                del pids_array[pid]
            else:
                pid += 1
        pid_str = "\n".join(pids_array)

    with open(config.extern["pid"], "w") as folder:
        folder.write(pid_str)
