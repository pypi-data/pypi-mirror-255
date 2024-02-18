#!/usr/bin/env python
# -*- coding: utf-8 -*-

def int_to_roman(int_input: int) -> str:
    """
    Convert an integer to a Roman numeral.
    """
    if not isinstance(int_input, int):
        raise TypeError(f"expected integer, got {type(int_input)}")
    if not 0 < int_input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = []
    for i in range(len(ints)):
        count = int(int_input / ints[i])
        result.append(nums[i] * count)
        int_input -= ints[i] * count
    return ''.join(result)


if __name__ == '__main__':
    res = int_to_roman(20)
    print(res)

# -
