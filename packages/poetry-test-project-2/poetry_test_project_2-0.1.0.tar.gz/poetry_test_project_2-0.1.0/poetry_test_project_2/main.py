"""
Created on 10/02/2024

Author: Joost Berkhout (VU, email: joost.berkhout@vu.nl)

Description:
"""

from random_module import random_function


def test_function():
    print('This is a test function 2.')
    print(random_function(1, 2))


if __name__ == "__main__":
    print('Is it a module or a script?')
    test_function()
