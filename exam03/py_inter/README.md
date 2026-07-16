py_inter
py_inter.py
Suggest Exercise
Help grow this exam bank
Suggest a new subject, report a wrong brief, or flag outdated text. Short Google form.
✕

Assignment
Write a function that returns a string with the characters that appear
in both strings, without repetitions. Characters are added in the order
they appear in the first string.

Function signature
def inter(s1: str, s2: str) -> str:

Examples
Input
inter("hello", "world")
Output
"lo"
Input
inter("banana", "band")
Output
"ban"
Input
inter("abcabc", "bc")
Output
"bc"
Input
inter("abc", "xyz")
Output
""
Input
inter("", "abc")
Output
""