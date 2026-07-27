def is_costas_array(arr: list[int]) -> bool:
    n = len(arr)
    
    if sorted(arr) != list(range(1, n + 1)) and sorted(arr) != list(range(n)):
        return False

    for dist in range(1, n):
        row_diffs = set()
        for i in range(n - dist):
            diff = arr[i + dist] - arr[i]
            if diff in row_diffs:
                return False  
            row_diffs.add(diff)
            
    return True


costas_4 = [7, 6, 13, 1, 2, 12, 9, 3, 5, 11, 14, 10, 15, 4, 8]
print(f"{costas_4} is valid: {is_costas_array(costas_4)}")  

