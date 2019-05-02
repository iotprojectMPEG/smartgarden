#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulated wind sensor.
"""

import numpy as np

INTENSITY = [(0, 3), (4, 7), (8, 12)]


def get_data():
    intensity = np.random.choice([0, 1, 2], p=[0.7, 0.27, 0.03])
    minimum = INTENSITY[intensity][0]
    maximum = INTENSITY[intensity][1]
    return np.random.randint(minimum, maximum+1)


def main():
    for i in range(30):
        wind = get_data()
        print('Wind: %d kn' %(wind))


if __name__ == '__main__':
    main()
