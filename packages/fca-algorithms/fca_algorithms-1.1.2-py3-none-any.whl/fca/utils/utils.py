def inverse_range(length, stop=-1):
    """helper function to iterate in an inverse order
    """
    return range(length - 1, stop, -1)


def is_in(elem, array):
    """
    Given an `elem` and an ordered array, it returns True and its index if the element is in there,
    False, None otherwise
    """
    low = 0
    high = len(array)
    while low < high:
        mid = (low + high) // 2
        if array[mid] < elem:
            low = mid + 1
        else:
            high = mid

    if 0 <= low < len(array) and array[low] == elem:
        return True, low
    return False, None


def lower_bound(elem, array):
    """returns the index in which you should insert the element `elem` to keep the order
    """
    low = 0
    high = len(array)
    while low < high:
        mid = (low + high) // 2
        if array[mid] < elem:
            low = mid + 1
        else:
            high = mid

    return low


def insert_ordered(elem, array):
    """inserts `elem` in `array` in an index that keeps the order
    """
    array.insert(lower_bound(elem, array), elem)


def insert_ordered_unique(elem, array):
    """inserts `elem` in `array` in an index that keeps the order only if the elem is not yet present
    """
    idx = lower_bound(elem, array)
    if idx < len(array) and array[idx] == elem:
        return
    array.insert(idx, elem)


def swap(array, i, j):
    array[i], array[j] = array[j], array[i]


def remove_if_exists(elem, array: list):
    """removes the element `elem` in array in O(1) by swapping its position with the last one
    """
    try:
        i = array.index(elem)
    except ValueError:
        return
    swap(array, i, -1)
    array.pop()


SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'  # outside the function so that it mallocs only once (?)
def to_subscript(number):
    if number < 0:
        return ValueError(f"{number} should be positive or zero")

    res = list(str(number))
    i = len(res) - 1
    while i >= 0:
        res[i] = SUBSCRIPTS[int(res[i])]
        i -= 1
    return ''.join(res)


integer_numbers = {
    '₀': '0',
    '₁': '1',
    '₂': '2',
    '₃': '3',
    '₄': '4',
    '₅': '5',
    '₆': '6',
    '₇': '7',
    '₈': '8',
    '₉': '9',

}  # outside the function so that it mallocs only once (?)
def from_subscript(number):
    res = []
    i = 0
    while i < len(number):
        res.append(integer_numbers[number[i]])
        i += 1
    return int(''.join(res))
