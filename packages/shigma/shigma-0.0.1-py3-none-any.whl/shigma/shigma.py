"""
Copyright (c) 2024 Henryk Popiołek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from math import prod


def sigma_not(n: int, a_i: str, i: int) -> int or float:
    """
    n: int, a_i: str, i: int

    :param n: The upper limit.
    :param a_i: The expression. It has to be a string and is executed like
    regular Python script, so it can include the variables "i", "n" and other
    variables outside of this scope.
    :param i: The lower limit.
    :return: The result of a sigma notation where "n" is placed above, "i" is
    placed below and "a_i" is placed as the expression.

    If you didn't understand this docstring, I advise you learn more about
    sigma notation.
    """
    arr: list[float or int] = []

    for i in range(i, n + 1):
        element = eval(a_i)
        arr.append(element)

    return sum(arr)


def pi_not(n: int, a_i: str, i: int) -> int or float:
    """
    n: int, a_i: str, i: int

    :param n: The upper limit.
    :param a_i: The expression. It has to be a string and is executed like
    regular Python script, so it can include the variables "i", "n" and other
    variables outside of this scope.
    :param i: The lower limit
    :return: The result of a pi notation where "n" is placed above, "i" is
    placed below and "a_i" is placed as the expression.

    If you didn't understand this docstring, I advise you learn more about
    pi notation.
    """
    arr: list[float or int] = []

    for i in range(i, n + 1):
        element = eval(a_i)
        arr.append(element)

    return prod(arr)


Σ = sigma_not
Π = pi_not
