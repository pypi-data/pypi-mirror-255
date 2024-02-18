from numpy import linspace, unique, median, percentile, mean
from math import floor, ceil, sqrt


def group_1D_to_2D(edges):
    result = []
    prev = edges[0]
    for i in range(1, len(edges)):
        result.append([prev, edges[i]])
        prev = edges[i]
    return result


def group_2D_to_1D(edges):
    result = [edges[0][0]]
    for e in edges:
        result.append(e[1])
    return result


def degroup_2D(x, edges):
    """
    Transform list of observations between edges.
    Each element in edges must contain start end end.
    The length of edges must be equal to the length of x
    """
    assert len(x) == len(edges)

    data = []
    for i, xx in enumerate(x):
        data += linspace(edges[i][0], edges[i][1], xx + 2).tolist()[1:-1]
    return data


def degroup(x, groups):
    """
    !!! Use with caution, depending on the goal, this might not do what you want!
    Transform grouped data to ungrouped data within intervals (no endpoints).
    Assumes data is uniformly distributed in each interval.

    Parameters
    ==========

    x : list
        1D or 2D list of data to be ungrouped

    groups : list
        List of edge points in each interval. Each element can consist of a single or two edge values.
        Can either be a single list for all lists of observations or individual lists for each.

    Possible groups
    ==========
    One grouping, single edges. E.g. 3 intervals with distance 1:
        [1,2,3,4]

    One grouping, double edges. E.g. 3 intervals with distance 1:
        [[1,2], [2,3], [3,4]]

    Multiple groupings, single edges. E.g. 2 groupings with 3 intervals with distance 1:
        [[1,2,3,4], [1,2,3,4]]

    Multiple grouping, double edges. E.g. 2 groupings with 3 intervals with distance 1:
        [[[1,2], [2,3], [3,4]], [[1,2], [2,3], [3,4]]]
    """

    data = []
    if hasattr(groups[0], "__iter__"):
        if hasattr(groups[0][0], "__iter__"):
            assert len(groups) == len(x)
            for i, xx in enumerate(x):
                data.append(degroup_2D(xx, groups[i]))
            return data

        if len(groups[0]) == 2:
            if hasattr(x[0], "__iter__"):
                assert len(x[0]) == len(groups)
                for xx in x:
                    data.append(degroup_2D(xx, groups))
                return data
            else:
                return degroup_2D(x, groups)
        else:
            assert len(x) == len(groups)
            for i, xx in enumerate(x):
                data.append(degroup_2D(xx, group_1D_to_2D(groups[i])))
            return data

    if hasattr(x[0], "__iter__"):
        assert len(x[0]) + 1 == len(groups)
        for xx in x:
            data.append(degroup_2D(xx, group_1D_to_2D(groups)))
        return data
    else:
        return degroup_2D(x, group_1D_to_2D(groups))


def group(x: list, groups):
    """
    Group observations in intervals open on the lower limit, i.e. ]a,b] where a <= b
    """
    if not hasattr(groups[0], "__iter__"):
        groups = group_1D_to_2D(groups)

    x.sort()
    idx = 0
    outliers = 0
    while idx < len(x) and x[idx] <= groups[0][0]:
        outliers += 1
        idx += 1

    result = [0] * len(groups)
    for i, g in enumerate(groups):
        while idx < len(x) and x[idx] <= g[1]:
            result[i] += 1
            idx += 1

    outliers += len(x) - idx - 1
    if outliers > 0:
        Warning(f"{outliers} observations were no inside group intervals.")
    return result


class FrequencyTable:
    observation: list
    total: int
    hyppighed: list
    frekvens: list
    kumuleret_frekvens: list

    def __init__(self, x: list):
        self.total = len(x)
        hyp = unique(x, return_counts=True)
        self.observation = hyp[0].tolist()
        self.hyppighed = hyp[1].tolist()
        self.init_freq()

    def init_freq(self):
        self.frekvens = []
        self.kumuleret_frekvens = []
        kf = 0
        for i in range(len(self.observation)):
            f = self.hyppighed[i] / self.total * 100
            self.frekvens.append(f)
            kf += f
            self.kumuleret_frekvens.append(kf)

    def __str__(self):
        names = ["Observation", "Hyppighed", "Frekvens %", "Kumuleret frekvens %"]
        if isinstance(self, FrequencyTableGrouped):
            names[0] = "Observationsinterval"
        s = "| "
        lens = []
        for n in names:
            s += f"{n} | "
            lens.append(len(n))
        s = s[:-1]
        s += "\n| "
        for n in range(len(names)):
            s += "-" * (lens[n]-1) + ": | "
        s += "\n| "
        for i in range(len(self.observation)):
            for k, n in enumerate([self.observation, self.hyppighed, self.frekvens, self.kumuleret_frekvens]):
                if hasattr(n[i], "__iter__") and len(n[i]) == 2:
                    if type(n[i][0]) == float:
                        stub = f"] {n[i][0]:.5} ;"
                    else:
                        stub = f"] {n[i][0]} ;"
                    s += " " * (floor(lens[k] / 2) - len(stub)) + stub
                    if type(n[i][1]) == float:
                        stub = f" {n[i][1]:.5} ]"
                    else:
                        stub = f" {n[i][1]} ]"
                    s += stub + " " * (floor(lens[k] / 2) - len(stub)) + " | "
                elif type(n[i]) == float:
                    s += f"{n[i]:>{lens[k]}.5} | "
                else:
                    s += f"{n[i]:>{lens[k]}} | "
            if i < len(self.observation) - 1:
                s += "\n| "
        return s


class FrequencyTableGrouped(FrequencyTable):
    def __init__(self, x: list, groups: list):
        self.total = sum(x)
        self.observation = []
        self.hyppighed = x

        if hasattr(groups[0], "__iter__"):
            assert len(groups[0]) == 2
            assert len(groups) == len(x)
            for g in groups:
                self.observation.append(g)
        else:
            assert len(groups) == len(x) + 1
            for i in range(len(groups) - 1):
                self.observation.append([groups[i], groups[i + 1]])

        self.init_freq()


def frekvenstabel(x, groups=[], show=True):
    """
    Calculate count, frequency and cumulative frequency of grouped or ungrouped data
    """
    assert not hasattr(x[0], "__iter__")
    if groups == []:
        table = FrequencyTable(x)
    else:
        table = FrequencyTableGrouped(x, groups)
    if show:
        print(table)
    return table


def kvartiler(data: list, n=[0, 1, 2, 3, 4]):
    """
    Calculate quartiles where Q2 is the median and Q1 and Q3 is the medians of the lower and higher halves, respectively.
    If the number of observations is odd the middle observation is not consideres during the calculation of Q1 and Q3.

    Parameters
    ==========
    n : list, optional
        Only quartiles with index in n is returned. Must be integers between 0 and 4 (inclusive)
    """
    data.sort()

    l2 = len(data) // 2
    lower = data[0:l2]
    higher = data[-l2:]
    results = [min(data), median(lower), median(data), median(higher), max(data)]
    return [results[i] for i in n]


percentile._implementation.__defaults__ = (None, None, False, "inverted_cdf", False)


def group_percentile(data, groups, q):
    """
    Calculate percentiles in groups (assuming uniform distribution between edges)
    """
    f = frekvenstabel(data, groups, show=False)
    if not hasattr(q, "__iter__"):
        q = [q]
    results = []
    for qq in q:
        i = next(i for i, v in enumerate(f.kumuleret_frekvens) if v >= qq)
        if i == 0:
            x1 = 0
        else:
            x1 = f.kumuleret_frekvens[i - 1]
        results.append(
            ((f.observation[i][1] - f.observation[i][0]) / (f.kumuleret_frekvens[i] - x1)) * (qq - x1)
            + f.observation[i][0]
        )
    if len(results) == 1:
        return results[0]
    return results


def group_mean(data, groups):
    return mean(degroup(data, groups))


def group_var(data, groups, ddof=0):
    f = frekvenstabel(data, groups, show=False)
    m = group_mean(data, groups)
    sum = 0
    for i, o in enumerate(f.observation):
        sum += ((o[0] + o[1]) / 2 - m) ** 2 * f.hyppighed[i]
    return sum / (f.total - ddof)


def group_std(data, groups, ddof=0):
    return sqrt(group_var(data, groups, ddof))


if __name__ == "__main__":
    # t = frekvenstabel([8, 3, 2, 1, 1, 2, 3, 4])
    # print(t.frekvens)
    # print(t.hyppighed)
    # print(t.observation)
    # print(t.kumuleret_frekvens)
    # t = frekvenstabel([8, 3, 2, 1], [1, 2, 3, 4, 5])
    # t = frekvenstabel([8, 3, 2, 1], [[1, 2], [2, 3], [3, 4], [4, 5]])
    # print(t.observation)
    # print(kvartiler([1,1,1,3,7,8]))
    # print(kvartiler([1,1,3,7,8],[1,2,3]))
    # print(percentile([1, 1, 1, 3, 7, 8], [20, 50, 80], method="inverted_cdf"))
    # print(percentile([1, 1, 1, 3, 7, 8], [20, 50, 80]))
    print(group_mean([1, 2, 3, 1], [1, 2, 3, 4, 5]))
    print(group_var([1, 2, 3, 1], [1, 2, 3, 4, 5], ddof=1))
    print(group_var([1, 2, 3, 1], [1, 2, 3, 4, 5]))
    print(group_std([1, 2, 3, 1], [1, 2, 3, 4, 5], ddof=1))
    print(group_std([1, 2, 3, 1], [1, 2, 3, 4, 5]))
    print(group_percentile([1, 2, 3, 1], [1, 2, 3, 4, 5], [25, 50, 75]))
    # frekvenstabel([1, 2, 3, 1], [1, 2, 3, 4, 5])
