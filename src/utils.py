def binary_search(array, target):
    start = 0
    end = len(array) - 1
    target = target.lower()

    while start <= end:
        mid = (start + end) // 2
        element = array[mid].lower()
        if len(element) > len(target):
            element = element[:len(target)]
        if element < target:
            start = mid + 1
        elif element > target:
            end = mid - 1
        else:
            return mid
    return None
