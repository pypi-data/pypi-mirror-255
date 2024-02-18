import os
import yaml
from stax.stack import Stack

script_dir = os.path.dirname(os.path.realpath(__file__))
yaml_file_path = os.path.join(script_dir, "token.yml")

with open(yaml_file_path, "r") as file:
    token = yaml.safe_load(file)


def execute_commands(line, stacks):
    line = line.strip()

    if not line:
        return

    tokens = line.split()

    if len(tokens) == 1 and tokens[0].rstrip(token["END"]) == token["EXIT"]:
        exit()

    elif len(tokens) == 1 and tokens[0].endswith(token["END"]):
        stack_name = tokens[0][:-1]
        stacks[stack_name] = Stack()

    else:
        command = tokens[0]
        if command == token["PUSH"]:
            try:
                value = eval(" ".join(tokens[1:-1]))
            except NameError:
                value = " ".join(tokens[1:-1])
            stack_name = tokens[-1][:-1]
            stacks[stack_name].push(value)
        elif command == token["POP"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].pop()
        elif command == token["PRINT"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].print()
        elif command == token["ADD"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].add()
        elif command == token["SUBT"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].subtract()
        elif command == token["MULT"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].multiply()
        elif command == token["DIV"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].divide()
        elif command == token["MOD"]:
            stack_name = tokens[-1][:-1]
            stacks[stack_name].mod()
