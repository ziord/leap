"""
:copyright: Copyright (c) 2020 Jeremiah Ikosin (@ziord)
:license: MIT, see LICENSE for more details
"""

from leap.goto import goto

# noinspection PyUnresolvedReferences,PyStatementEffect
@goto
def build_list(begin_val, end_val):
    """
    >>> build_list(1, 20)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    >>> build_list(1, 10)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    lst = []
    ind = begin_val
    label .begin
    if ind == end_val:
        goto .end
    lst.append(ind)
    ind += 1
    goto .begin
    label .end
    return lst

# noinspection PyUnresolvedReferences,PyStatementEffect
@goto
def print_list(lst):
    """
    >>> print_list([1, 2, 3, 5, 6, 7])
    1
    2
    3
    5
    6
    7
    """
    i = 0
    label .start
    item = lst[i]
    print(item)
    if i == len(lst) - 1:
        goto .end
    else:
        i += 1
        goto .start
    label .end


# noinspection PyUnresolvedReferences,PyStatementEffect
@goto
def loop(condition, function, args):
    """
    >>> def foo(arg):
    ...     print(arg)
    ...     arg -= 1
    ...     return arg
    >>> loop(lambda x: x > 0, foo, 8)
    8
    7
    6
    5
    4
    3
    2
    1
    """
    check = function(args)
    label .start
    if condition(check):
        check = function(check)
        goto .start
    else:
        goto .end
    label .end

# noinspection PyUnresolvedReferences,PyStatementEffect
@goto
def print_list2(lst):
    """
    >>> print_list2([1, 2, 3, 5, 6, 7])
    1
    2
    3
    5
    6
    7
    """
    i = 0
    label .start
    item = lst[i]
    print(item)
    if i == len(lst) - 1:
        goto .end
    else:
        i += 1
        goto .start
    label .end

# noinspection PyUnresolvedReferences,PyStatementEffect
@goto(debug=False)
def build_list2(begin_val, end_val):
    """
    >>> build_list2(1, 20)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    >>> build_list2(1, 10)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    lst = []
    ind = begin_val
    label .begin
    if ind == end_val:
        goto .end
    lst.append(ind)
    ind += 1
    goto .begin
    label .end
    return lst


# noinspection PyUnresolvedReferences,PyStatementEffect
def max_labels_error():
    """
    >>> try:
    ...     @goto(max_labels=2)
    ...     def err():
    ...         label .start1
    ...         label .start2
    ...         label .start3
    ... except Exception as e:
    ...     print(e)
    Too many labels in function. Max allowed: 2
    """


# noinspection PyUnresolvedReferences,PyStatementEffect
def max_gotos_error():
    """
    >>> try:
    ...     @goto(max_gotos=2)
    ...     def err():
    ...         goto .start1
    ...         goto .start2
    ...         goto .start3
    ... except Exception as e:
    ...     print(e)
    Too many gotos in function. Max allowed: 2
    """


# noinspection PyUnresolvedReferences,PyStatementEffect
def label_not_found_error():
    """
    >>> try:
    ...     @goto
    ...     def err():
    ...         goto .start1
    ...         print("Hi there!")
    ... except Exception as e:
    ...     print(e)
    Label `start1` was not found.
    """
