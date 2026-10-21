def bracket_validator(s: str) -> bool:
    stack = []

    coppie = {')': '(', ']': '[', '}': '{'}

    for c in s:
        if c in "([{":
            stack.append(c)
        elif c in ")]}":
            if not stack or stack[-1] != coppie[c]:
                return False
            stack.pop()

    return len(stack) == 0





# --- Tests based on your examples ---
print(bracket_validator("()"))            # True
print(bracket_validator("()[]{}"))        # True
print(bracket_validator("(]"))            # False
print(bracket_validator("([)]"))          # False
print(bracket_validator("{[]}"))          # True
print(bracket_validator("hello(world)"))  # True
print(bracket_validator("((())"))         # False
print(bracket_validator(""))              # True
