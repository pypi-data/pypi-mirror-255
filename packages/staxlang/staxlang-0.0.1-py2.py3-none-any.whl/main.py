from sys import argv
from stax.command_handler import execute_commands


def main():
    if len(argv) > 2:
        print("Usage: stack [file].stax")
        exit()

    stacks = {}

    if len(argv) == 1:
        print(f"Stax interactive shell v(0.0.1)")
        while True:
            print(">>> ", end="")
            line = input()
            execute_commands(line, stacks)

    try:
        with open(argv[1]) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("File not found")
        exit()

    for line in lines:
        execute_commands(line, stacks)


if __name__ == "__main__":
    main()
