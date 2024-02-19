# SPDX-FileCopyrightText: 2023-present JACS <jacs@zbc.dk>
#
# SPDX-License-Identifier: MIT

from sympy import N, solve, expand, factor, nsolve, symbols, Matrix, Function, Piecewise, limit, diff, integrate, dsolve
from spb import plot_list, plot, plot_implicit, plot_geometry, plot3d_list, plot3d_implicit
from numpy import mean, median, var, std
from math import pi, sqrt

from .trigonometry import Sin, Cos, Tan, aSin, aCos, aTan
from .vector import plot_vector, plot_vector_field, plot3d_line, plot3d_plane
from .stats import group, degroup, frekvenstabel, kvartiler, percentile, group_std, group_mean, group_percentile, group_var
from .stat_plot import boxplot, plot_bars, plot_sum, plot_hist
from .regression import regression_poly, regression_power, regression_exp
from .ode import plot_ode
from .spb_defaults import _configure_spb

a, b, c, d, e, f, g, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = symbols(
    'a b c d e f g i j k l m n o p q r s t u v w x y z', real=True
)

_configure_spb()