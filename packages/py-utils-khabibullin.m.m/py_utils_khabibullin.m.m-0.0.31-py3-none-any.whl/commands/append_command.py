import json
from typing import Optional
from commands.const import DATA_FILE, COMMANDS, ID, COMMAND, LABELS


def append_command(
    *, id_num: Optional[int] = None, command: str, lables: Optional[list[str]]
) -> list[int]:
    if not command:
        raise ValueError("command is required.")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    commands = data[COMMANDS]

    if id_num is None:
        id_num = max([c[ID] for c in commands]) + 1

    commands.append(
        {
            ID: id_num,
            COMMAND: command,
            LABELS: lables,
        }
    )

    data[COMMANDS] = commands

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
