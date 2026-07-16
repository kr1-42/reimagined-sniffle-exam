#01
Level 1
py_bracket_validator
py_bracket_validator.py
Suggest Exercise
Help grow this exam bank
Suggest a new subject, report a wrong brief, or flag outdated text. Short Google form.
✕
Assignment
Write a function that checks if the brackets in a string are valid.
A string is valid if every opening bracket has a matching closing bracket
in the correct order.

Allowed brackets: (), [], {}

Function signature
def bracket_validator(s: str) -> bool:



Examples
Input
bracket_validator("()")
Output
True
Input
bracket_validator("()[]{}")
Output
True
Input
bracket_validator("(]")
Output
False
Input
bracket_validator("([)]")
Output
False
Input
bracket_validator("{[]}")
Output
True
Input
bracket_validator("hello(world)")
Output
True
Input
bracket_validator("((())")
Output
False
Input
bracket_validator("")
Output
True

