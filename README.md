<div align="center">
    <img alt="leap image" src="assets/leap_256x256.png"/>
    <div>
        <a href="https://www.python.org/">
                <img alt="built with python" src="https://img.shields.io/badge/built%20with-python-blue.svg?style=plastic" >
        </a>
        <a href="https://github.com/ziord/leap/blob/master/LICENSE.txt">
            <img alt="Leap License" src="https://img.shields.io/github/license/ziord/leap?style=plastic" >
        </a>
        <a href="https://www.python.org/downloads/">
                <img alt="python versions (3.6-3.7)" src="https://img.shields.io/badge/python-3.6|3.7-blue.svg?style=plastic">
        </a>
        <a href="https://github.com/ziord/leap/issues" >
            <img alt="issues" src="https://img.shields.io/github/issues/ziord/leap?style=plastic">
        </a>
        <a href="https://github.com/ziord/leap/stargazers">
            <img alt="stars" src="https://img.shields.io/github/stars/ziord/leap?style=plastic">
        </a>
        <a href="https://github.com/ziord/leap/network/members">
            <img alt="forks" src="https://img.shields.io/github/forks/ziord/leap?style=plastic">
        </a>
    </div>
</div>

## Leap

Leap is an _experimental_ package written to enable the utilization of [C-like goto](https://en.cppreference.com/w/cpp/language/goto) statements in Python functions. It currently supports only Python 3.6 and 3.7. 

## Examples
Labels are added using a `label` keyword, and gotos are added using a `goto` keyword.
Here is a simple function that prints the contents of a list, using the `goto` keyword.

```python
from leap.goto import goto

@goto
def print_list(lst):
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

# test
print_list(range(5))

# this outputs
0
1
2
3
4
```

We can also utilize the `goto` decorator, if we need to pass arguments, to perform checks.

Below is a simple function that builds a list given a start value an end value, and an optional step value.
Here, formal arguments `max_gotos` and `max_labels` are sentries that ensures the maximum number of `goto`
 and `label` statements in `build_list()` does not exceed the actual parameter values. If it does, an exception is raised accordingly.

`debug` (`False` by default, only explicitly declared for example sake) is also set to `False` to disable internal-processing outputs.

```python
from leap.goto import goto

@goto(debug=False, max_gotos=3, max_labels=3)
def build_list(begin_val, end_val, step=1):
    lst = []
    val = begin_val
    label .begin
    if val >= end_val:
        goto .end
    lst.append(val)
    val += step
    goto .begin
    label .end
    return lst

print(build_list(1, 10))  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Below is a simple function `err()` that will fail at _decoration_ time.

```python
from leap.goto import goto

@goto(max_labels=2)
def err():
    label .start1
    label .start2
    label .start3


# Traceback (most recent call last):
# ...
# LabelLimitError: Too many labels in function. Max allowed: 2
```
The exception was triggered because `max_labels` was exceeded. The same applies to `goto` statements (in this case we have a `GotoLimitError`).

Duplicate labels are also not allowed (this can lead to some form of ambiguity).

```python
from leap.goto import goto

@goto(max_labels=3)
def err2():
    label .start
    label .start


# Traceback (most recent call last):
# ...
# DuplicateLabelError: Duplicate labels found: `start`
```

Labels that are not declared in a function cannot be referenced in a `goto` statement.

Below is a simple example that will fail.

```python
from leap.goto import goto

@goto(max_labels=2)
def err3():
    x = 0
    goto .end
    label .start


# Traceback (most recent call last):
# ...
# LabelNotFoundError: Label `end` was not found.
```
Functions `err()`, `err2()`, and `err3()` will fail even _before_ any of them are called.


### Why?
Why not? I mean, it's a perfect excuse to test bytecode editing/rewriting possibilities in Python. 


### Tests
See the [tests](https://github.com/ziord/leap/blob/master/tests) folder for tests and other examples.
To run the tests, simply cd to the `Leap` directory, and do:
`python -m tests.test -v`


### Limitations
Only functions/methods are supported (may be easily inferable from the decorator syntax).
Nested functions/methods are not supported, that is, labels cannot be declared in external or enclosing functions and referenced in another function be it inner or enclosing.


### Installation
Clone this repo, and do:

`cd leap` <br/> `python setup.py install`


### Bugs/Features
Please [file an issue](https://github.com/ziord/leap/issues).


### License
[MIT](https://github.com/ziord/leap/blob/master/LICENSE.txt)