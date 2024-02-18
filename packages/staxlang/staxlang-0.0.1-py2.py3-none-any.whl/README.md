# Staxlang

A [ZISC](https://en.wikipedia.org/wiki/No_instruction_set_computing) inspired stack based language / interpreter written in python, providing simple instruction sets for executing programs

## Features
- **Stack based:** Uses variable number of Stacks to store items of varying data types in memory.
- **Postfix notation:** Use `PUSH`, `POP`, `PRINT`, and arithmetic keywords to perform instructions on the stack using [postfix notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation).

## Installation
- Install `python` and `pip` using your OS package manager
- Run

    $ `pip install staxlang`

## Usage
- Create a test file
`test.stax`
```
stack;
PUSH "Hello World" stack;
PRINT stack;
```
Execute the program by running
    
    stax test.stax

output:
```
Hello World
```

- You can also run the `stax` program just by itself. This will open in repl mode and you can run arbitrary commands in the interpreter.
```
>>> stack;
>>> PUSH "Hello World!" stack;
>>> PRINT stack;
Hello World
>>>
```

## Examples

### Hello world
Code:
```
stack;                       # Creating a stack of name "stack"
PUSH "Hello World" stack     # Pushing "Hello World" to the stack
PRINT stack;                 # Printing the topmost variable in the stack
```
output:
```
Hello World!
```

### Calculation
Code:
```
stack;                       # Creating a stack of name "stack"
PUSH 1 stack;                # Pushing 1 to the stack 
PUSH 2 stack;                # Pushing 2 to the stack
ADD stack;                   # Removing the top 2 elements in the stack and pushing its sum to the stack
PRINT stack;                 # Printing the topmost variable in the stack
```
output:
```
3
```

## Keywords
Here are a list of keywords in the language
|Keyword|Description                                                  |Syntax             |
|-------|-------------------------------------------------------------|-------------------|
|`PUSH` |Push a value onto the stack                                  |`PUSH VAL ST_NAME;`|
|`POP`  |Pop the topmost value from the stack                         |`POP ST_NAME;`     |
|`PRINT`|Print the top most element in the stack                      |`PRINT ST_NAME;`   |
|`ADD`  |Pop the top two elements in the stack and push the sum       |`ADD ST_NAME;`     |
|`SUBT` |Pop the top two elements in the stack and push the difference|`SUBT ST_NAME;`    |
|`MULT` |Pop the top two elements in the stack and push the product   |`MULT ST_NAME;`    |
|`DIV`  |Pop the top two elements in the stack and push the quotient  |`DIV ST_NAME;`     |
|`MOD`  |Pop the top two elements in the stack and push the modulus   |`MOD ST_NAME;`     |
|`EXIT` |Exit the program|`EXIT;` |

Any other keyword used is considered as the name of a new stack

Legend:
|KEY    |VALUE                           |
|-------|--------------------------------|
|VAL    |Any value                       |
|ST_NAME|Name of an already defined Stack|
