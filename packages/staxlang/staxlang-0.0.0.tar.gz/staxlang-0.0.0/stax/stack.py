class Stack:
    def __init__(self) -> None:
        self.stack = []

    def push(self, n: int) -> None:
        self.stack += [n]

    def pop(self) -> int:
        return self.stack.pop()

    def print(self) -> None:
        print(self.stack[-1])

    def add(self) -> int:
        a = self.pop()
        b = self.pop()
        c = a + b

        self.push(c)
        return c

    def subtract(self) -> int:
        a = self.pop()
        b = self.pop()
        c = a - b

        self.push(c)
        return c

    def multiply(self) -> int:
        a = self.pop()
        b = self.pop()
        c = a * b

        self.push(c)
        return c

    def divide(self) -> int:
        a = self.pop()
        b = self.pop()
        c = a // b

        self.push(c)
        return c

    def mod(self) -> int:
        a = self.pop()
        b = self.pop()
        c = a % b

        self.push(c)
        return c
