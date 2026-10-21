py_whisper_cipher
py_whisper_cipher.py
Suggest Exercise
Help grow this exam bank
Suggest a new subject, report a wrong brief, or flag outdated text. Short Google form.
✕

Assignment
Write a function that creates a Caesar cipher by shifting letters in a
string by a given amount.
Non-alphabetic characters should remain unchanged.
The shift can be negative (shift left).

Function signature
def whisper_cipher(text: str, shift: int) -> str:

Examples
Input
whisper_cipher("hello", 3)
Output
"khoor"
Input
whisper_cipher("Hello World!", 1)
Output
"Ifmmp Xpsme!"
Input
whisper_cipher("xyz", 3)
Output
"abc"
Input
whisper_cipher("ABC123def", 5)
Output
"FGH123ijk"
Input
whisper_cipher("", 10)
Output
""
Input
whisper_cipher("abc", -3)
Output
"xyz"