from gym_cas import *
from sympy.core.numbers import Float
from spb import MB


def test_linear():
    f, p = regression_poly([1, 2, 3], [3, 6, 12], 1, show=False, return_plot=True)
    assert callable(f)
    assert type(f(2.0)) == Float
    assert isinstance(p, MB)


def test_poly():
    f, p = regression_poly([1, 2, 3, 4], [3, 6, 12, 4], 2, show=False, return_plot=True)
    f = regression_poly([1, 2, 3, 4], [3, 6, 12, 4], 2, show=False)
    assert callable(f)
    assert type(f(2.0)) == Float
    assert isinstance(p, MB)


def test_power():
    f, p = regression_power([1, 2, 3], [3, 6, 12], show=False, return_plot=True)
    f = regression_power([1, 2, 3], [3, 6, 12], show=False)
    assert callable(f)
    assert type(f(2.0)) == Float
    assert isinstance(p, MB)


def test_exp():
    f, r2, p = regression_exp([1, 2, 3], [3, 6, 12], return_r2=True, return_plot=True, show=False)
    f, r2 = regression_exp([1, 2, 3], [3, 6, 12], return_r2=True, show=False)
    f = regression_exp([1, 2, 3], [3, 6, 12], show=False)
    assert callable(f)
    assert type(f(2.0)) == Float
    assert type(r2) == float
    assert isinstance(p, MB)
