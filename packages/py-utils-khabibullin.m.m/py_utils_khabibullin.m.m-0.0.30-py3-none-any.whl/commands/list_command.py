import os
import json
from prettytable import PrettyTable

from commands.const import DATA_FILE, ID, LABELS, COMMAND, COMMANDS


def list_commands(labels: [str] = None):
    table = PrettyTable(["id", "command", "labels"])

    print(DATA_FILE)

    labels_set = set(labels or [])
    print(f"Labels: {labels_set}")

    if not os.path.isfile(DATA_FILE):
        print("commands -d -k the_key_to_decrypt")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        commands = data[COMMANDS]

        for cmd in commands:
            command_labels = set(cmd[LABELS]) if LABELS in cmd else set()
            if labels_set and not labels_set.intersection(command_labels):
                continue
            table.add_row([cmd[ID], cmd[COMMAND], ", ".join(command_labels)])

    print(table)
