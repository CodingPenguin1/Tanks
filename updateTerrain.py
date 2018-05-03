# -*- coding: utf-8 -*-
#==============================================================================
# Title: Update Terrain
# Author: Ryan J. Slater
# Date: 5/2/2018
#==============================================================================

def update(array, xstart=0, xstop=-1):
    """
    update(array)

    Drops all -1s in an array as low as possible

    Parameters
    ----------

    array : 2D numpy array

    Returns
    ----------

    2D numpy array
        Modified array
    """

    if xstop == -1:
        xstop = len(array[0])

    for col in range(xstart, xstop):
        pointCount = 0
        for row in range(len(array)):
            if array[row][col] == -1:
                pointCount += 1
                array[row][col] = 0
        for row in range(len(array)-1, len(array)-1-pointCount, -1):
            array[row][col] = -1

    return array