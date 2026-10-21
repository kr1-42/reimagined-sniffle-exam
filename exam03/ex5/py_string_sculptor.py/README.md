py_string_sculptor
py_string_sculptor.py
Suggest Exercise
Help grow this exam bank
Suggest a new subject, report a wrong brief, or flag outdated text. Short Google form.
✕
Assignment
Write a function that transforms a string by alternating the case of
alphabetic characters only.
Non-alphabetic characters remain unchanged and are NOT counted in the
alternation index.
The first alphabetic character should be lowercase, the second uppercase, etc.
Spaces reset the alternation (next alpha after a space is lowercase again).

Function signature
<!-- def string_sculptor(text: str) -> str: -->

Examples
Input
string_sculptor("hello")
Output
"hElLo"
Input
string_sculptor("Hello World")
Output
"hElLo wOrLd"
Input
string_sculptor("abc123def")
Output
"aBc123DeF"
Input
string_sculptor("Python3.9!")
Output
"pYtHoN3.9!"
Input
string_sculptor("")
Output
""