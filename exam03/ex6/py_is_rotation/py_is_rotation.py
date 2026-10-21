def is_rotation(arr1: list, arr2: list) -> bool:
    if len(arr1) != len(arr2):
        return False
    
    if len(arr1) == 0:
        return True
        
    n = len(arr1)
    for i in range(n):
        rotated_arr1 = arr1[i:] + arr1[:i]
        
        if rotated_arr1 == arr2:
            return True
            
    return False

print(is_rotation([1, 2, 3, 4, 5], [4, 5, 1, 2, 3]))
print(is_rotation([1, 2, 3, 4, 5], [5, 1, 2, 3, 4]))
print(is_rotation([1, 2, 3], [3, 2, 1]))
print(is_rotation([1, 2], [1, 2, 3]))
print(is_rotation([], []))
