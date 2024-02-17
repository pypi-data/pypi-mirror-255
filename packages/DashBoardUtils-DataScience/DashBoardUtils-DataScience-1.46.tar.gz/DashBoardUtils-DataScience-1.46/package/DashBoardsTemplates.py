# bokeh version for diffrent graphs pairs from generated data

"""Dashboared templates for visualising data

    Returns:
        ploat: figure
    """

import random
import math
import collections
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange


def export_graphs_hist(chuncks):
    """_summary_

    Args:
        chuncks (_type_): _description_

    Returns:
        _type_: _description_
    """

    obj_lists = []
    for _x in chuncks:
        fruits = list(_x.values())[0]["lables"]
        counts = list(_x.values())[0]["counts"]
        _p = figure(
            x_range=fruits,
            height=350,
            title=list(_x.keys())[0],
            toolbar_location=None,
            tools="",
        )
        _p.vbar(x=fruits, top=counts, width=0.9)
        _p.xgrid.grid_line_color = None
        _p.y_range.start = 0
        obj_lists.append(_p)
    return "exported {}".format(str(len(chuncks))), obj_lists


def export_graphs_line(chuncks):
    """_summary_

    Args:
        chuncks (_type_): _description_

    Returns:
        _type_: _description_
    """

    obj_lists = []
    for _x in chuncks:
        fruits = list(range(len(list(_x.values())[0]["lables"])))
        counts = list(_x.values())[0]["counts"]
        graph = figure(title=list(_x.keys())[0])
        graph.line(fruits, counts, line_width=2)
        graph.xaxis.axis_label = ",".join(list(_x.values())[0]["lables"])
        obj_lists.append(graph)
    return "exported {}".format(str(len(chuncks))), obj_lists


def export_graphs_pie_charts(chuncks):
    """_summary_

    Args:
        chuncks (_type_): _description_

    Returns:
        _type_: _description_
    """

    obj_lists = []
    for i, _x in enumerate(chuncks):
        graph = figure(title=list(_x.keys())[0])
        sectors = list(_x.values())[0]["lables"]
        percentages = list(_x.values())[0]["counts"]
        radians = [math.radians((percent / 100) * 360) for percent in percentages]
        start_angle = [math.radians(0)]
        prev = start_angle[0]
        for _i in radians[:-1]:
            start_angle.append(_i + prev)
        prev = i + prev
        end_angle = start_angle[1:] + [math.radians(0)]
        _x = 0
        _y = 0
        radius = 1
        color = [
            "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
            for i in range(len(sectors))
        ]
        for _i in range(len(sectors)):
            graph.wedge(
                _x,
                _y,
                radius,
                start_angle=start_angle[_i],
                end_angle=end_angle[_i],
                color=color[_i],
                legend_label=sectors[_i],
            )
        obj_lists.append(graph)
    return "exported {}".format(str(len(chuncks))), obj_lists


def data_verience_whole_table(chuncks):
    """_summary_

    Args:
        chuncks (_type_): _description_

    Returns:
        _type_: _description_
    """
    newlist = [list(x.keys())[0] for x in chuncks]
    return {i: newlist.count(i) for i in newlist}


def build_dogged_from(data, title):
    """_summary_

    Args:
        data (_type_): _description_
        title (_type_): _description_

    Returns:
        _type_: _description_
    """

    label_data = data[list(data.keys())[0]]
    catagories = list(data.keys())[1:]
    _x = [(label, catagory) for label in label_data for catagory in catagories]
    counts = sum(zip(*[data[xa] for xa in catagories]), ())
    source = ColumnDataSource(data=dict(x=_x, counts=counts))
    _p = figure(
        x_range=FactorRange(*_x),
        height=500,
        title=title,
        toolbar_location=None,
        tools="",
        output_backend="svg",
        width=1000,
    )
    _p.vbar(x="_x", top="counts", width=0.9, source=source, line_color="white")
    _p.y_range.start = 0
    _p.x_range.range_padding = 0.1
    _p.xaxis.major_label_orientation = 1
    _p.xgrid.grid_line_color = None
    return _p


def export_graphs_nested_color_mapped(chuncks):
    """_summary_

    Args:
        chuncks (_type_): _description_

    Returns:
        _type_: _description_
    """
    ploat_ = [(list(x.keys())[0], list(x.values())) for x in chuncks]
    _c = collections.defaultdict(list)
    for _a, _b in ploat_:
        _c[_a].extend(_b)  # add to existing list or create a new one

    list_2 = list(_c.items())
    label_unique = []
    for _xs in list_2:
        for _xp in _xs[1]:
            label_unique += _xp["lables"]
    core_labels = [x[0] for x in ploat_]
    dummy_label_list = {}
    for _x in list(set(label_unique)):
        dummy_label_list[_x] = list(range(len([x[0] for x in ploat_])))
    final_data = {"core": list(set(core_labels))}
    for _im, _x in enumerate(list(set(core_labels))):
        dummy_labels = []
        for _d in ploat_:
            if _d[0] == _x:
                dummy_labels.append(_d)
        dummy_labels_to_dict = collections.defaultdict(list)
        for _p, _m in dummy_labels:
            dummy_labels_to_dict[_p].extend(_m)
        listw = list(dummy_labels_to_dict.items())
        for _sx in listw:
            data23 = {"lables": [], "counts": []}
            formatted = {}
            for xsd in _sx[1]:
                data23["lables"] += xsd["lables"]
                data23["counts"] += xsd["counts"]
            for _xw in range(len(data23["lables"])):
                if list(formatted.keys()) == []:
                    formatted[data23["lables"][_xw]] = data23["counts"][_xw]
                if data23["lables"][_xw] not in list(formatted.keys()):
                    formatted[data23["lables"][_xw]] = data23["counts"][_xw]
                else:
                    formatted[data23["lables"][_xw]] += data23["counts"][_xw]
            corew = []
            for xsww in core_labels:
                if xsww not in corew:
                    corew.append(xsww)
            datasq = {}
            for k, _v in formatted.items():
                index = corew.index(_sx[0])
                dummy_lab = [0 for x in corew]
                dummy_lab[index] = _v
                datasq[k] = dummy_lab
            final_data.update(datasq)
    return (
        "exported {}".format(str(len(chuncks))),
        build_dogged_from(final_data, "Test Title"),
    )
