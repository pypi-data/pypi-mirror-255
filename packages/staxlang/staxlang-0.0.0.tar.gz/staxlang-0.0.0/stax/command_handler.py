from .stack import Stack


def execute_commands(file_path):
    try:
        with open(file_path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("File not found")
        exit()

    stacks = {}

    for line in lines:
        line = line.strip()

        if not line:
            continue

        tokens = line.split()

        if len(tokens) == 1 and tokens[0].endswith(";"):
            stack_name = tokens[0][:-1]
            stacks[stack_name] = Stack()

        else:
            command = tokens[0]
            if command == "PUSH":
                try:
                    value = eval(" ".join(tokens[1:-1]))
                except NameError:
                    value = " ".join(tokens[1:-1])
                stack_name = tokens[-1][:-1]
                stacks[stack_name].push(value)
            elif command == "POP":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].pop()
            elif command == "PRINT":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].print()
            elif command == "ADD":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].add()
            elif command == "SUBT":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].subtract()
            elif command == "MULT":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].multiply()
            elif command == "DIV":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].divide()
            elif command == "MOD":
                stack_name = tokens[-1][:-1]
                stacks[stack_name].mod()
