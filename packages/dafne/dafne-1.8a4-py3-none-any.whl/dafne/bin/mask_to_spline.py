#  Copyright (c) 2022 Dafne-Imaging Team
import os
import sys
import importlib
import time
from bisect import bisect

import imageio.v3 as imageio
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ..ui.ContourPainter import ContourPainter
from ..utils import mask_utils
from ..utils.mask_to_spline import mask_to_splines, mask_average, mask_to_trivial_splines, \
    masks_splines_to_splines_masks
from ..utils.pySplineInterp import SplineInterpROIClass

matplotlib.use("Qt5Agg")

def tik():
    global t0
    t0 = time.perf_counter()


def tok(msg=''):
    global t0
    t = time.perf_counter() - t0
    print(f'Execution time {msg} (ms)', t*1000)


def main():
    # Load image
    im1 = imageio.imread('mask_tests/two_masks.png')
    m1 = im1[:, :, 0] > 0

    im2 = imageio.imread('mask_tests/two_masks_2.png')
    m2 = im2[:, :, 0] > 0

    spline_list_1 = mask_to_trivial_splines(m1, spacing=4)
    spline_list_2 = mask_to_trivial_splines(m2, spacing=4)
    print('Number of splines', len(spline_list_1))
    index1 = 1
    index2 = 2


    splines_list = masks_splines_to_splines_masks([spline_list_1, spline_list_2])
    out_mask = np.zeros(m1.shape, dtype=np.uint8)
    for subroi_spline in splines_list:
        out_spline = SplineInterpROIClass()
        spline1 = subroi_spline[0]
        spline2 = subroi_spline[1]

        current_index = 3
        for knot1, knot2 in zip(spline1.knots, spline2.knots):
            out_spline.addKnot(
                ((knot1[0] * (index2 - current_index) + knot2[0] * (current_index - index1)) / (index2 - index1),
                 (knot1[1] * (index2 - current_index) + knot2[1] * (current_index - index1)) / (index2 - index1)), True)
        out_mask += out_spline.toMask(m1.shape)


    plt.imshow(out_mask)
    plt.gcf().canvas.draw()
    c1 = ContourPainter('red', 2)
    c1.add_roi(out_spline)
    c1.add_roi(spline1)
    c1.add_roi(spline2)
    c1.draw(plt.gca())


    plt.show()