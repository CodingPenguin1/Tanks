#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#==============================================================================
# Title: Generate Random Function
# Author: Ryan J. Slater
# Date: 4/17/2018
#==============================================================================

import matplotlib.pyplot as plt

x = []
y = []
coef = [6, 3, -7, 2]

for i in range(1080):
    x.append(i)
    y.append((i-coef[0])*(i-coef[1]))

plt.plot(x, y, linewidth=2.0)