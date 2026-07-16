py_twist_sequence
py_twist_sequence.py
Suggest Exercise
Help grow this exam bank
Suggest a new subject, report a wrong brief, or flag outdated text. Short Google form.
✕

Assignment
Write a function that rotates an array to the right by k positions.
Rotating right by k means the last k elements move to the front.

Function signature
def twist_sequence(arr: list[int], k: int) -> list[int]:

Examples
Input
twist_sequence([1,2,3,4,5], 2)
Output
[4,5,1,2,3]
Input
twist_sequence([1,2,3], 1)
Output
[3,1,2]
Input
twist_sequence([1,2,3,4], 0)
Output
[1,2,3,4]
Input
twist_sequence([1,2,3], 5)
Output
[2,3,1]
Input
twist_sequence([], 3)
Output
[]