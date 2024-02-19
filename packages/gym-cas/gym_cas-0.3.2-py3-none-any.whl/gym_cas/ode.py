from spb import plot_vector
from sympy import diff, classify_ode, solve
from sympy.abc import y

def plot_ode( ode, f, x_range, f_range, points=15, **kwargs):
    """
    Plot a 1st order linear ODE direction field.

    Parameters
    ==========

    ode: expression 
        1st order linear ODE

    f: Function
        Dependent variable to be plotted

    x_range: tuple
        Range tuple of independent variable (x, start, stop)

    f_range: tuple
        Range tuple of dependent variable (f, start, stop) 

    kwargs : see plot_vector_field (or plot_vector in spb)
        
    """
    assert('1st_linear' in classify_ode(ode))
    
    kwargs.setdefault("use_cm",False)
    kwargs.setdefault("scalar",False)
    kwargs.setdefault("quiver_kw",{"color": "black", "headwidth": 5})

    x = x_range[0]
    df = solve(ode,diff(f(x),x))[0].replace(f(x),y)

    f_range = (y,f_range[1],f_range[2])
            
    return plot_vector([1,df],x_range, f_range,n=points,**kwargs)


if __name__ == "__main__":
    from sympy import Function
    from sympy.abc import t
    f = Function('f')
    p = plot_ode(diff(f(t),t)-5*f(t)/t,f,(t,0,100),(f,0,100))