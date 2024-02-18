from sys import argv
from .command_handler import execute_commands


def main():
    if len(argv) != 2:
        print("Usage: stack [file].stk")
        exit(1)

    execute_commands(argv[1])


if __name__ == "__main__":
    main()
