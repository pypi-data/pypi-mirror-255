import argparse
from commands.decrypt import decrypt
from commands.encrypt import encrypt

from commands.list_command import list_commands
from commands.append_command import append_command


def main():
    parser = argparse.ArgumentParser(
        prog="commands",
        description="list of commands",
    )

    # parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-l", "--labels", action="append")
    parser.add_argument("-a", "--append", action="store_true")
    parser.add_argument("-c", "--command", action="store")
    parser.add_argument("--id", action="store")
    parser.add_argument("-e", "--encrypt", action="store_true")
    parser.add_argument("-d", "--decrypt", action="store_true")
    parser.add_argument("-k", "--key", action="store")

    args = parser.parse_args()

    if args.append:
        append_command(
            id_num=int(args.id) if args.id is not None else None,
            command=args.command,
            lables=args.labels,
        )
    elif args.encrypt:
        encrypt(args.key)
    elif args.decrypt:
        decrypt(args.key)
    else:
        list_commands(labels=args.labels)
