def binary_search(array, target):
    start = 0
    end = len(array) - 1

    while start <= end:
        mid = (start + end) // 2
        if array[mid].lower() < target.lower():
            start = mid + 1
        elif array[mid].lower() > target.lower():
            end = mid - 1
        else:
            return mid
    return None
