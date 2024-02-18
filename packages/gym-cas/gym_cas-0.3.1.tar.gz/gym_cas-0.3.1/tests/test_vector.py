from gym_cas import *
from gym_cas.vector import Arrow3DSeries
from sympy.abc import u, t
from spb.series import Parametric3DLineSeries, ParametricSurfaceSeries, Arrow2DSeries
from spb import MB


def test_plot_vector_2d():
    p = plot_vector([1, 2], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], Arrow2DSeries)
    assert s[0].get_data() == (0, 0, 1, 2)


def test_plot_vector_3d():
    p = plot_vector([1, 2, 3], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], Arrow3DSeries)
    assert not s[0].is_streamlines
    assert (s[0].get_data() == [[0], [0], [0], [1], [2], [3]]).all()
    assert s[0].get_label(False) == ""


def test_plot3d_line():
    p = plot3d_line(Matrix([1 + t, 2 - t, 3 + t]), (t, 0, 1), show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], Parametric3DLineSeries)
    assert s[0].get_data()[0][0] == 1
    assert s[0].get_label(False) == "(t + 1, 2 - t, t + 3)"


def test_plot3d_plane():
    p = plot3d_plane(Matrix([1 + t - u, 2 - t + u, 3 + t]), (t, 0, 1), (u, 0, 1), show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], ParametricSurfaceSeries)
    assert s[0].get_data()[0][0][0] == 1
    assert s[0].get_label(False) == "(t - u + 1, -t + u + 2, t + 3)"
