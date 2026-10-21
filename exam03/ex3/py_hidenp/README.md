#05
Level 3
py_hidenp
py_hidenp.py
Suggest Exercise
Help grow this exam bank
Suggest a new subject, report a wrong brief, or flag outdated text. Short Google form.
✕

Assignment
Write a function that checks if the string 'small' is a subsequence
of 'big'. A subsequence means all characters of 'small' appear in 'big'
in the same order, but not necessarily consecutively.
Function is case-sensitive.

Function signature
def hidenp(small: str, big: str) -> bool:

Examples
Input
hidenp("abc", "a1b2c3")
Output
True
Input
hidenp("ace", "abcde")
Output
True
Input
hidenp("aec", "abcde")
Output
False
Input
hidenp("", "abc")
Output
True
Input
hidenp("abc", "ab")
Output
False
Input
hidenp("aaaa", "aaa")
Output
False
Input
hidenp("sing","subsequence testing")
Output
True