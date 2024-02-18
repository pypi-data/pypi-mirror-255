from spb import plot_vector, plot3d_parametric_line, plot3d_parametric_surface
from spb.graphics import graphics, arrow_2d
from spb.series import BaseSeries, Vector2DSeries, Vector3DSeries
from spb.defaults import TWO_D_B, THREE_D_B
from spb.utils import _check_arguments, _plot_sympify
from spb.plot_functions.functions_2d import _set_labels, _create_generic_data_series
from numpy import array
from sympy import Matrix, N
from warnings import filterwarnings

# Filter xlim, ylim, and zlim warnings for 3D quiver
filterwarnings("ignore", module="spb", lineno=514)
filterwarnings("ignore", module="spb", lineno=521)
filterwarnings("ignore", module="spb", lineno=535)

# Rename spb plot_vector to plot_vector_field
plot_vector_field = plot_vector

# Based on
# https://sympy-plot-backends.readthedocs.io/en/latest/tutorials/tut-6.html
# https://github.com/Chrillebon/DTUMathTools/blob/main/src/dtumathtools/dtuplot/quiverplot.py
# https://github.com/Davide-sd/sympy-plot-backends/blob/master/spb/series.py#L2857
# https://github.com/Davide-sd/sympy-plot-backends/blob/master/spb/backends/matplotlib/renderers/vector2d.py

class Arrow3DSeries(BaseSeries):
    is_3D = True
    normalize = False
    is_3Dvector = True
    is_streamlines = False
    is_slice = False
    _allowed_keys = []

    def __init__(self, start, direction, label="", **kwargs):
        """
        start: Start position of vector or list of vectors
        direction: Direction of vector or list of vectors
        label: Label to be shown for the series

        **kwargs : Keyword arguments to be passed on
        """
        super().__init__(**kwargs)
        self._set_use_quiver_solid_color(**kwargs)

        if hasattr(start[0], '__iter__'):
            self.start = start
            self.direction = direction
        else:
            self.start = [start]
            self.direction = [direction]

        if label != "":
            self.rendering_kw.setdefault("label", label)

    def _set_use_quiver_solid_color(self, **kwargs):
        self.use_quiver_solid_color = (
            True
            if ("scalar" not in kwargs.keys())
            else (False if (not kwargs["scalar"]) or (kwargs["scalar"] is None) else True)
        )

    def get_data(self):
        return array(
            [[x[i] for x in self.start] for i in range(3)] + [[x[i] for x in self.direction] for i in range(3)]
        )

    def __str__(self):
        if len(self.start) == 1:
            return f"3D Vector: s{self.start[0]} v{self.direction[0]}"

        s = "3D Vectors: "
        for i in range(len(self.start)):
            s += f"{i}: s{self.start[i]} v{self.direction[i]} "
        return s


THREE_D_B.renderers_map.update({Arrow3DSeries: THREE_D_B.renderers_map[Vector3DSeries]})


def check_dims(v, s=None):
    if hasattr(v[0], '__iter__') or type(v[0]) == Matrix:
        d = len(v[0])
        if d != 2 and d != 3:
            raise TypeError(f"First vector was neither 2D or 3D")
        for vv in v:
            if len(vv) != d:
                raise TypeError("A vector didn't match the dimensions of the first vector")
            if s != None:
                for ss in s:
                    if len(ss) != d:
                        raise TypeError("A starting point didn't match the dimensions of the vectors")
        return d, True

    d = len(v)
    if d != 2 and d != 3:
        TypeError("The vector was neither 2D nor 3D")
    if s != None and s != d:
        TypeError("Starting point and vector must have same dimensions")
    return d, False


def calc_limits(v, s):
    kw = ["xlim", "ylim", "zlim"]
    result = {}

    if not hasattr(v[0], '__iter__'):
        v = [v]
        s = [s]

    for d in range(len(v[0])):
        d_min = v[0][d] + s[0][d] if v[0][d] + s[0][d] < s[0][d] else s[0][d]
        d_max = v[0][d] + s[0][d] if v[0][d] + s[0][d] > s[0][d] else s[0][d]
        for i in range(len(v)):
            if v[i][d] + s[i][d] > s[i][d]:
                nextmax = v[i][d] + s[i][d]
                nextmin = s[i][d]
            else:
                nextmin = v[i][d] + s[i][d]
                nextmax = s[i][d]
            if nextmin < d_min:
                d_min = nextmin
            if nextmax > d_max:
                d_max = nextmax
        extra = (d_max - d_min) / 10
        result[kw[d]] = (d_min - extra, d_max + extra)
    return result


def plot_vector(*args, **kwargs):
    """
    Plot 2D or 3D vectors or list of vectors. Typical usage examples:

    - Plotting a vector with (0,0) as starting point:
        `plot_vector(v, **kwargs)`

    - Plotting multiple vectors with custom starting points:
        `plot_vector([s1,s2], [v1,v2], **kwargs)`

    Parameters
    ==========

    args :
        s : Vector, or Matrix/list/tuple of vector each with 2 or 3 elements.
            Represents the starting point(s) of the vector(s) to be plotted.

        v : Vector, or Matrix/list/tuple of vector each with 2 or 3 elements.
            Represents the vector(s) to be plotted.

    label : str, optional
        The name of the vector(s) to be shown on the label.

    quiver_kw : dict
        A dictionary of keywords/values which is passed to the backend quivers-
        plotting function to customize the appearance. Refer to the plotting
        library (backend) manual for more informations.

    rendering_kw : list of dicts, optional
        A list of dictionaries of keywords/values which is passed to the
        backend's functions to customize the appearance.

    show : boolean
        The default value is set to `True`. Set show to `False` and
        the function will not display the plot. The returned instance of
        the `Plot` class can then be used to save or display the plot
        by calling the `save()` and `show()` methods respectively.

    size : (float, float), optional
        A tuple in the form (width, height) to specify the size of
        the overall figure. The default value is set to `None`, meaning
        the size will be set by the backend.

    title : str, optional
        Title of the plot. It is set to the latex representation of
        the expression, if the plot has only one expression.

    xlabel, ylabel, zlabel : str, optional
        Labels for the x-axis, y-axis, z-axis, respectively.
        ``zlabel`` is only available for 3D plots.

    xlim, ylim, zlim : (float, float), optional
        Denotes the axis limits, `(min, max)`, visible in the chart.
        ``zlim`` is only available for 3D plots
    """
    if len(args) == 1:
        v = args[0]
        dim, lst = check_dims(v)

        if lst:
            for i in range(len(v)):
                if type(v[i]) == Matrix:
                    v[i] = [float(N(x)) for x in v[i]]
            s = [[0] * dim] * len(v)
        else:
            if type(v) == Matrix:
                v = [float(N(x)) for x in v]
            s = [0] * dim

    elif len(args) == 2:
        s = args[0]
        v = args[1]
        dim, lst = check_dims(v, s)
        if lst:
            for i in range(len(v)):
                if type(v[i]) == Matrix:
                    v[i] = [float(N(x)) for x in v[i]]
            for i in range(len(s)):
                if type(s[i]) == Matrix:
                    s[i] = [float(N(x)) for x in s[i]]
        if type(v) == Matrix:
            v = [float(N(x)) for x in v]
        if type(s) == Matrix:
            s = [float(N(x)) for x in s]

    else:
        raise TypeError(f"plot_vector() expects 1 or 2 arguments ({len(args)} were given)")

    limits = calc_limits(v, s)
    for lim in limits:
        kwargs.setdefault(lim, limits[lim])

    show = kwargs.get("show", True)
    kwargs.setdefault("aspect", "equal")
    kwargs.setdefault("xlabel", "x")
    kwargs.setdefault("ylabel", "y")
    if kwargs.get("label", False):
        kwargs.setdefault("legend", True)
    else:
        kwargs.setdefault("legend", False)

    if dim == 2:
        global_labels = kwargs.pop("label", [])
        global_rendering_kw = kwargs.pop("rendering_kw", None)
        arrows = []
        if hasattr(s[0], "__iter__"):
            for start, dir in zip(s, v):
                arrows.extend(arrow_2d(start, dir, **kwargs))
        else:
            arrows.extend(arrow_2d(s, v, **kwargs))
        _set_labels(arrows, global_labels, global_rendering_kw)
        gs = _create_generic_data_series(**kwargs)
        return graphics(*arrows, gs, **kwargs)

        # backend = kwargs.get("backend", TWO_D_B)
        # p = backend(Arrow2DSeries(s, v, **kwargs), **kwargs)
    elif dim == 3:
        kwargs.setdefault("zlabel", "z")
        backend = kwargs.get("backend", THREE_D_B)
        p = backend(Arrow3DSeries(s, v, **kwargs), **kwargs)
    else:
        raise ValueError("Mixing 2D vectors with 3D vectors is not allowed.")

    if show:
        p.show()
    return p


def plot3d_line(*args, **kw_args):
    """
    Plots a 3D parametric line.

    Typical usage examples are in the followings:

    - Plotting a single expression.
        `plot3d_line(line, range, **kwargs)`
    - Plotting multiple expressions with the same ranges.
        `plot3d_line(line_1, line_2, ..., range, **kwargs)`
    - Plotting multiple expressions with different ranges.
        `plot3d_line((line_1, range1), (line_2, range2), ..., **kwargs)`
    - Plotting multiple expressions with custom labels.
        `plot3d_line((line_1, range1, label1), (line_2, range2, label2), ..., **kwargs)`

    Parameters
    ==========

    args :
        line : 3D list or matrix
            Expressions representing x, y, and z component of the parametric function.

    For more details and other parameters see documentation of plot3d_parametric_line
    """

    kw_args.setdefault("use_cm", False)

    args = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 1)
    for i in range(len(plot_expr)):
        if plot_expr[i][3] == None:
            if plot_expr[i][2] == None:
                plot_expr[i] = (plot_expr[i][0][0], plot_expr[i][0][1], plot_expr[i][0][2], plot_expr[i][1])
            else:
                plot_expr[i] = (
                    plot_expr[i][0][0],
                    plot_expr[i][0][1],
                    plot_expr[i][0][2],
                    plot_expr[i][1],
                    plot_expr[i][2],
                )
        else:
            plot_expr[i] = (
                plot_expr[i][0][0],
                plot_expr[i][0][1],
                plot_expr[i][0][2],
                plot_expr[i][1],
                plot_expr[i][2],
                plot_expr[i][3],
            )
    return plot3d_parametric_line(*plot_expr, **kw_args)


def plot3d_plane(*args, **kw_args):
    """
    Plots a 3D parametric plane.

    Typical usage examples are in the followings:

    - Plotting a single expression.
        `plot3d_plane(plane, range_s, range_t, **kwargs)`
    - Plotting multiple expressions with the same ranges.
        `plot3d_plane(plane_1, plane_2, range_s, range_t, **kwargs)`
    - Plotting multiple expressions with different ranges.
        `plot3d_plane((plane_1, range_s1, range_t1), (plane_2, range_s1, range_t1), **kwargs)`
    - Plotting multiple expressions with different ranges and labels.
        `plot3d_plane((plane_1, range_s1, range_t1, label1), (plane_2, range_s1, range_t1, label2), **kwargs)`

    Note: it is important to specify both the ranges.

    Parameters
    ==========

    args :
        plane : 3D list or matrix
            Expressions representing x, y, and z component of the parametric function.

    For more details and other parameters see documentation of plot3d_parametric_surface
    """
    kw_args.setdefault("use_cm", False)

    args = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 2)
    for i in range(len(plot_expr)):
        if plot_expr[i][3] == None:
            if plot_expr[i][2] == None:
                plot_expr[i] = (plot_expr[i][0][0], plot_expr[i][0][1], plot_expr[i][0][2], plot_expr[i][1])
            else:
                plot_expr[i] = (
                    plot_expr[i][0][0],
                    plot_expr[i][0][1],
                    plot_expr[i][0][2],
                    plot_expr[i][1],
                    plot_expr[i][2],
                )
        else:
            plot_expr[i] = (
                plot_expr[i][0][0],
                plot_expr[i][0][1],
                plot_expr[i][0][2],
                plot_expr[i][1],
                plot_expr[i][2],
                plot_expr[i][3],
            )
    return plot3d_parametric_surface(*plot_expr, **kw_args)


if __name__ == "__main__":
    # a = plot_vector((0, 0), (5, 5), show=False, label="test")
    # b = plot_vector([4, 4], show=False)
    # c = plot_vector([(2, 3), (1, 1)], label="(2,3) og (1,1)", show=False)
    # plot_vector([(0, 0), (1, 1)],[(2, 3), (1, 1)])
    # (a + b + c).show()
    # print(a)
    # print(c)

    # d = plot_vector([5, 5, 5], label="hej", show=False)
    # e = plot_vector([1, 1, 1], Matrix([1, 2, 3]), label="matrix", show=False)
    # f = plot_vector([Matrix([0, 1, 1]), Matrix([1, 1, 0])], label="matrix", show=False)
    # (d + e + f).show()

    # print(d)

    from sympy.abc import s, t

    a = Matrix([1, 2, 3])
    b = Matrix([1, 1, 1])
    line = a + t * b
    # plot3d_line(line,(t,0,10))
    # plot3d_line( line, b+t*a, (t,0,10))
    # plot3d_line((line,(t,0,20)),(b+t*a, (t,0,10)))
    # plot3d_line((line, (t, 0, 20), "hej"), (b + t * a, (t, 0, 10), "hej2"))

    c = Matrix([0, 0, 1])
    plane = a + t * b + s * c
    # plot3d_plane(plane, (t, 0, 10), (s, -10, 0))

    # plot3d_plane( plane , (t, 0, 10), (s, -10, 0))
    # plot3d_plane(plane, t*a + b + s * c, (t, 0, 10), (s, -10, 0))
    # plot3d_plane((plane,(t, 0, 10), (s, -10, 0)), (t*a + b + s * c, (t, 0, 10), (s, -10, 20)))
    plot3d_plane((plane, (t, 0, 10), (s, -10, 0), "p1"), (t * a + b + s * c, (t, 0, 10), (s, -10, 20), "p2"))
