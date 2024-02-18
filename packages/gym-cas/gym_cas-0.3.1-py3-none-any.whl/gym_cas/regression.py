from numpy.polynomial import Polynomial
from numpy import corrcoef
from sympy import simplify, ln, exp
from sympy.abc import x
from spb import plot, plot_list


def reg_poly(X, Y, deg):
    p = Polynomial.fit(X, Y, deg)
    ps = simplify(p(x))
    return lambda xin: ps.subs(x, xin)


def reg_pow(X, Y, _):
    X_LOG = [float(ln(x).evalf()) for x in X]
    Y_LOG = [float(ln(y).evalf()) for y in Y]

    p = Polynomial.fit(X_LOG, Y_LOG, 1)
    ps = exp(p.convert().coef[0]) * x ** p.convert().coef[1]
    return lambda xin: ps.subs(x, xin)


def reg_exp(X, Y, _):
    Y_LOG = [float(ln(y).evalf()) for y in Y]

    p = Polynomial.fit(X, Y_LOG, 1)
    ps = exp(p.convert().coef[0]) * exp(p.convert().coef[1]) ** x
    return lambda xin: ps.subs(x, xin)


def regression(X, Y, deg, method, show=True, return_r2=False, return_plot=False):
    fun = method(X, Y, deg)
    YP = [float(fun(x)) for x in X]
    r2 = float(corrcoef(YP, Y)[0][1] ** 2)
    if show or return_plot:
        p1 = plot_list(X, Y, is_point=True, show=False, title=f"Forklaringsgrad $R^2 = {r2:.3}$")
        p2 = plot(fun(x), show=False)
        plt = p1 + p2 
        avg_step_x = (max(X) - min(X)) / len(X)
        plt.xlim = (min(X) - avg_step_x, max(X) + avg_step_x)
        avg_step_y = (max(Y) - min(Y)) / len(Y)
        plt.ylim = (min(Y) - avg_step_y, max(Y) + avg_step_y)
        if show:
            plt.show()
        if return_plot:
            if return_r2:
                return fun, r2, plt
            return fun, plt

    if return_r2:
        return fun, r2

    return fun


def regression_poly(X, Y, deg, show=True, return_r2=False, return_plot=False):
    """
    Polynomial regression.

    Parameters
    ==========

    X,Y : list
        Datapoints 

    deg : int
        Degree of polynomial. Use deg = 1 for linear interpolation
    
    show : bool, default = True
        Whether to show plot
    
    return_r2: bool, default = False
        Whether to return the r2 value
    
    return_plot: bool, default = False
        Whether to return the plot
    """
    return regression(X, Y, deg, reg_poly, show, return_r2, return_plot)


def regression_power(X, Y, show=True, return_r2=False, return_plot=False):
    """
    Power regression.

    Parameters
    ==========

    X,Y : list
        Datapoints 
    
    show : bool, default = True
        Whether to show plot
    
    return_r2: bool, default = False
        Whether to return the r2 value
    
    return_plot: bool, default = False
        Whether to return the plot
    """
    return regression(X, Y, 1, reg_pow, show, return_r2, return_plot)


def regression_exp(X, Y, show=True, return_r2=False, return_plot=False):
    """
    Exponential regression.

    Parameters
    ==========

    X,Y : list
        Datapoints 
    
    show : bool, default = True
        Whether to show plot
    
    return_r2: bool, default = False
        Whether to return the r2 value
    
    return_plot: bool, default = False
        Whether to return the plot
    """
    return regression(X, Y, 1, reg_exp, show, return_r2, return_plot)

if __name__ == "__main__":
    f, p1 = regression_poly([1, 2, 3], [3, 6, 12], 1, show=False, return_plot=True)
    print(f(x))
    print(f(2.0))

    p, p2 = regression_poly([1, 2, 3, 4], [3, 6, 12, 4], 2, show=False, return_plot=True)
    print(p(x))
    print(p(2.0))

    f2, p3 = regression_power([1, 2, 3], [3, 6, 12], show=False, return_plot=True)
    print(f2(x))
    print(f2(2.0))

    f3, r2, p4 = regression_exp([1, 2, 3], [3, 6, 12],return_r2=True, return_plot=True,show=False)
    print(f3(x))
    print(f3(2.0))
    print(r2)

    (p1+p2+p3+p4).show()

