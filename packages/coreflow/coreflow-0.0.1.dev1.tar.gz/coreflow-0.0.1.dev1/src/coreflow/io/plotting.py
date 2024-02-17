from typing import Any, Optional, List, Set, Dict, Tuple, Union
import collections.abc

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns

import plotly.graph_objects as go
import plotly.subplots as subplots

import bokeh.plotting as bh
import bokeh.io as bh_io
import bokeh.models as bh_models
import bokeh.layouts as bh_layouts

from coreflow.utils.general import update_dict, extend_dict


class Plot:
    # plot relative permeabilities
    @staticmethod
    def plot_relperms(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        lin_scale: bool = True,
        log_scale: bool = True,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot relative permeabilities.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        lin_scale : boolean
            Whether to plot in linear scale
        log_scale : boolean
            Whether to plot in log scale
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        # update traces based on tag specific settings
        x, y = Plot.update_traces(
            x,
            y,
            tags={"water", "ref"},
            all_tags=True,
            opts=dict(
                name="krw (ref)",
                color="blue",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags={"oil", "ref"},
            all_tags=True,
            opts=dict(
                name="kro (ref)",
                color="red",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags={"gas", "ref"},
            all_tags=True,
            opts=dict(
                name="krg (ref)",
                color="green",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags="water",
            opts=dict(
                name="krw",
                color="blue",
                mode="lines",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags="oil",
            opts=dict(
                name="kro",
                color="red",
                mode="lines",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags="gas",
            opts=dict(
                name="krg",
                color="green",
                mode="lines",
            ),
        )

        if lin_scale and log_scale:
            fig = Plot.make_subplots(
                rows=1, cols=2, plot_with=kwargs.get("plot_with", "plotly")
            )
            sub_opts = dict(
                xaxis_title="water saturation",
                yaxis_title="relative permeability",
                xaxis_range=(0.0, 1.0),
                figure=fig,
                show=False,
            )
            sub_opts = update_dict(sub_opts, kwargs)

            # linear scale
            lin_sub_opts = sub_opts
            lin_sub_opts = update_dict(
                lin_sub_opts,
                dict(
                    title="kro, krw ( lin-scale )",
                    yaxis_type="linear",
                    yaxis_range=(0.0, 1.0),
                ),
            )
            Plot.plot(x, y, **lin_sub_opts, row=1, col=1)

            # log scale
            log_sub_opts = sub_opts
            log_sub_opts = update_dict(
                log_sub_opts,
                dict(
                    title="kro, krw ( log-scale )",
                    yaxis_type="log",
                    yaxis_range=None,
                ),
            )
            Plot.plot(x, y, **log_sub_opts, row=1, col=2)

            opts = dict(
                title="relative permeabilities",
                figure=fig,
            )
            opts = update_dict(opts, kwargs)
            return Plot.plot(None, None, **opts)
        else:
            opts = dict(
                title="relative permeabilities",
                xaxis_title="water saturation",
                yaxis_title="relative permeability",
                xaxis_range=(0.0, 1.0),
                yaxis_range=(0.0, 1.0) if lin_scale else None,
                yaxis_type="linear" if lin_scale else "log",
            )
            opts = update_dict(opts, kwargs)
            return Plot.plot(x, y, **opts)

    # plot capilalry pressure
    @staticmethod
    def plot_pc(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot capillary presssure.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        # update traces based on tag specific settings
        x, y = Plot.update_traces(
            x,
            y,
            tags="ref",
            opts=dict(
                color="blue",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags={"oil", "water"},
            all_tags=True,
            opts=dict(
                name="pcow",
                color="red",
                mode="lines",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags={"gas", "water"},
            all_tags=True,
            opts=dict(
                name="pcgw",
                color="red",
                mode="lines",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags={"gas", "oil"},
            all_tags=True,
            opts=dict(
                name="pcgo",
                color="red",
                mode="lines",
            ),
        )
        opts = dict(
            title="capillary pressure",
            xaxis_title="water saturation",
            yaxis_title="capillary pressure [ bar ]",
            xaxis_range=(0.0, 1.0),
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot injection schedule
    @staticmethod
    def plot_injection(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot injection schedule.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        # update traces based on tag specific settings
        x, y = Plot.update_traces(
            x,
            y,
            tags="water",
            opts=dict(
                name="water",
                color="blue",
                mode="lines+markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags="oil",
            opts=dict(
                name="oil",
                color="red",
                mode="lines+markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags="gas",
            opts=dict(
                name="gas",
                color="green",
                mode="lines+markers",
            ),
        )
        opts = dict(
            title="injection rates",
            xaxis_title="time [ hours ]",
            yaxis_title="injection rate [ cc/hour ]",
            chart_type="step",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot acceleration schedule
    @staticmethod
    def plot_acceleration(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot acceleration schedule.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="acceleration",
                color="red",
                mode="lines+markers",
            ),
        )
        opts = dict(
            title="acceleration",
            xaxis_title="time [ hours ]",
            yaxis_title="acceleration [ m/s/s ]",
            chart_type="step",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot pressure
    @staticmethod
    def plot_pressure(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot pressure drop over time.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags="ref",
            opts=dict(
                name="pressure measured",
                color="red",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="pressure calculated",
                color="blue",
                mode="lines",
            ),
        )
        opts = dict(
            title="differential pressure",
            xaxis_title="time [ hours ]",
            yaxis_title="pressure [bar]",
            color="blue",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot production
    @staticmethod
    def plot_production(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot production over time.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags="ref",
            opts=dict(
                name="production measured",
                color="red",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="production calculated",
                color="blue",
                mode="lines",
            ),
        )
        if flooding == "imbibition":
            title = "oil production"
        elif flooding == "drainage":
            title = "water production"
        else:
            title = "production"
        opts = dict(
            title=title,
            xaxis_title="time [ hours ]",
            yaxis_title="production [ cm3 ]",
            color="blue",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot saturation
    @staticmethod
    def plot_saturation(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot average saturation over time.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags="ref",
            opts=dict(
                name="saturation measured",
                color="red",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="saturation calculated",
                color="blue",
                mode="lines",
            ),
        )
        if flooding == "imbibition":
            title = "average water saturation"
        elif flooding == "drainage":
            title = "average oil saturation"
        else:
            title = "average saturation"
        opts = dict(
            title=title,
            xaxis_title="time [ hours ]",
            yaxis_title="saturation [ cm3/cm3 ]",
            yaxis_range=(-0.1, 1.1),
            color="blue",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot saturation profile
    @staticmethod
    def plot_saturation_profile(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot saturation profile over core.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags="ref",
            opts=dict(
                name="saturation measured",
                color="red",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="saturation calculated",
                color="blue",
                mode="lines",
            ),
        )
        if flooding == "imbibition":
            title = "water saturation profile"
        elif flooding == "drainage":
            title = "oil saturation profile"
        else:
            title = "saturation profile"
        opts = dict(
            title=title,
            xaxis_title="length [ cm ]",
            yaxis_title="saturation [ cm3/cm3 ]",
            yaxis_range=(0.0, 1.0),
            color="blue",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot solution
    @staticmethod
    def plot_solution(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot solution over time.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags="ref",
            opts=dict(
                name="measured",
                color="red",
                mode="markers",
            ),
        )
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="calculated",
                color="blue",
                mode="lines",
            ),
        )
        opts = dict(
            title="solution",
            xaxis_title="time [ hours ]",
            yaxis_title="value",
            color="blue",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # plot loss
    @staticmethod
    def plot_loss(
        self,
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        experiment_name: str = None,
        flooding: str = None,
        **kwargs,
    ):
        """
        Plot loss.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like
            y array-like
        experiment_name : str, default None
            Experiment name
        flooding : str, default None
            Flooding type: 'drainage' or 'imbibition'
        """
        x, y = Plot.update_traces(
            x,
            y,
            tags=None,
            opts=dict(
                name="calculated",
                color="blue",
                mode="lines+markers",
            ),
        )
        opts = dict(
            title="RMS",
            xaxis_title="index of simulation",
            yaxis_title="rms",
            color="blue",
        )
        opts = update_dict(opts, kwargs)
        return Plot.plot(x, y, **opts)

    # make subplots
    @staticmethod
    def make_subplots(
        rows: int = 1, cols: int = 1, plot_with: str = None, **kwargs
    ) -> Any:
        """
        rows : int, default 1
            Number of rows
        cols : int, default 1
            Number of columns
        plot_with : str, default 'plotly'
            Plot library, one of 'matplotlib', 'seaborn', 'plotly', 'bokeh'
        """
        nrows = rows or 1
        ncols = cols or 1
        if plot_with in {"matplotlib", "seaborn"}:
            # see, https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            return plt.subplots(nrows=nrows, ncols=ncols)
        elif plot_with in {"bokeh"}:
            return [[None for _ in range(ncols)] for _ in range(nrows)]
        # plotly
        # see, https://plotly.com/python/subplots/
        return subplots.make_subplots(
            rows=nrows,
            cols=ncols,
            subplot_titles=tuple(f"Plot {i+1}" for i in range(nrows * ncols)),
            **kwargs,
        )

    # get number of traces
    @staticmethod
    def get_num_traces(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        source: Union[Dict, pd.DataFrame] = None,
        **kwargs,
    ) -> int:
        """
        Get number of traces.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like or None
            y array-like
        source : dict, DataFrame, default None
            Data source, which allows to refer to x and y by DataFrame column or dictionary field name
        """
        if isinstance(x, tuple) or isinstance(y, tuple):
            if y is None:
                # case 1: (x,y)
                # case 2: ((x1,y1), (x2,y2), ..., (xn,yn))
                num_traces = sum(isinstance(t, tuple) for t in x) or 1
            else:
                # case 1: x=x, y=y
                # case 2: x=x, y=(y1, y2, ..., yn)
                # case 3: x=(x1, x2, ..., xn), y=(y1, y2, ..., yn)
                num_traces = max(len(t) if isinstance(t, tuple) else 1 for t in (x, y))
        elif x is not None or y is not None:
            num_traces = 1
        else:
            num_traces = 0
        return num_traces

    # get trace
    @staticmethod
    def get_trace(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        idx: int = 0,
        source: Union[Dict, pd.DataFrame] = None,
        **kwargs,
    ) -> Tuple[Any, Any]:
        """
        Get trace by id.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like or None
            y array-like
        idx : int, default 0
            trace index
        num_traces : int
            number of traces
        source : dict, DataFrame, default None
            Data source, which allows to refer to x and y by DataFrame column or dictionary field name
        """

        def _last_non_none(v):
            for item in v[idx::-1]:
                if item is not None:
                    return item
            else:
                return None

        def _get_trace(v):
            if not isinstance(v, tuple):
                return v
            return _last_non_none(v)

        if y is None:
            if any(isinstance(t, tuple) for t in x):
                trace = _get_trace(x)
                return trace[0], trace[1]
            return x[0], x[1]
        return _get_trace(x), _get_trace(y)

    @staticmethod
    def get_trace_tags(trace: Any):
        """
        Get trace tags.
        """
        if not isinstance(trace, collections.abc.Mapping):
            return set()
        tags = trace.get("tags", set())
        if tags is None:
            return set()
        elif not isinstance(tags, (list, set, tuple)):
            tags = {tags}
        else:
            tags = set(tags)
        # remove None
        return {item for item in tags if item is not None}

    @staticmethod
    def get_trace_values(trace: Any):
        """
        Get trace name.
        """

        # flatten array
        def flatten(v: Union[List, np.ndarray, Any]):
            if isinstance(v, list):
                for vi in v:
                    if isinstance(vi, list):
                        break
                else:
                    return v
                v_flat = []
                for vi in v:
                    v_flat.extend(vi)
                return v_flat
            elif isinstance(v, np.ndarray):
                return v.flatten() if v.ndim > 1 else v
            elif isinstance(v, (tuple, set)):
                return list(v)
            return [v]

        return (
            flatten(trace.get("values", None))
            if isinstance(trace, collections.abc.Mapping)
            else flatten(trace)
        )

    @staticmethod
    def get_trace_name(trace: Any, default: str = None):
        """
        Get trace name.
        """
        return (
            trace.get("name", None)
            if isinstance(trace, collections.abc.Mapping)
            else default
        )

    # update traces
    @staticmethod
    def update_traces(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        tags: Union[str, Tuple, List, Set] = None,
        source: Union[Dict, pd.DataFrame] = None,
        opts: Dict = None,
        all_tags: bool = True,
        overwrite: bool = False,
    ) -> Tuple[Any, Any]:
        """
        Update traces which math provided tag.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like or None
            y array-like
        source : dict, DataFrame, default None
            Data source, which allows to refer to x and y by DataFrame column or dictionary field name
        tags : str, tuple, list, default None
            trace tag(s). If None all tags will fit.
        all_tags : boolean, default False
            If true, math all tags, otherwise math at least one tag
        overwrite : boolean, default False
            If true, overwrite existing keys, otherwise don't
        opts : Dict
            Trace options
        """
        if not isinstance(tags, (list, set, tuple)) or tags is None:
            match_tags = {tags}
        else:
            match_tags = set(tags)

        def _update_trace(v: Any):
            if not isinstance(v, collections.abc.Mapping):
                return v
            trace_tags = Plot.get_trace_tags(v)
            if not all_tags and not any(
                t is None or t in trace_tags for t in match_tags
            ):
                return v
            elif all_tags and not all(t is None or t in trace_tags for t in match_tags):
                return v
            if overwrite:
                v = update_dict(v, opts)
            else:
                v = extend_dict(v, opts)
            return v

        def _update_traces(v):
            if not isinstance(v, tuple):
                return _update_trace(v)
            for item in v:
                item = _update_traces(item)
            return v

        return _update_traces(x), _update_traces(y) if y is not None else y

    # plot
    @staticmethod
    def plot(
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        source: Union[Dict, pd.DataFrame] = None,
        width: int = None,
        height: int = None,
        title: str = None,
        legend_title: str = None,
        xaxis_title: str = None,
        yaxis_title: str = None,
        xaxis_range: Union[Tuple, List] = None,
        yaxis_range: Union[Tuple, List] = None,
        xaxis_type: str = None,
        yaxis_type: str = None,
        chart_type: str = None,
        show_grid: str = None,
        show: bool = True,
        row: int = None,
        col: int = None,
        figure: Any = None,
        image_file: str = None,
        opts: Dict = None,
        plot_with: str = None,
        **kwargs,
    ) -> Any:
        """
        Plot data using one of the libraries, such as plotly(default), bokeh, matplotlib/seaborn.

        Parameters
        __________
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like or None
            y array-like
        source : dict, DataFrame, default None
            Data source, which allows to refer to x and y by DataFrame column or dictionary field name
        width : int, default None
            Plot width
        height : int, default None
            Plot height
        title : str, default ''
            Plot title
        legend_title : str, default None
            Legend title
        xaxis_title : str, default None
            X axis title
        yaxis_title : str, default None
            Y axis title
        xaxis_type : str, default 'linear'
            X axis type. One of 'linear', 'log', 'date', 'category', 'multicategory'
        yaxis_type : str, default 'linear'
            Y axis type. One of 'linear', 'log', 'date', 'category', 'multicategory'
        xaxis_range : tuple, list
            X axis range
        yaxis_range : tuple, list
            Y axis range
        chart_type : str, default 'line'
            Type of chart. One of 'marker', 'line', 'step'
        show_grid : str
            Show grid
        show : str, default None
            Show figure
        row : int
            Subplot row
        col : int
            Subplot column
        figure : Any
            Figure object. In case of 'matplotlib' it is fig, ax tuples
        image_file : str, default None
            Save plot file
        opts : dict, default None
            Plotting library specific properties
        plot_with : str, default 'plotly'
            Plot library, one of 'matplotlib', 'seaborn', 'plotly', 'bokeh'
        """
        if not isinstance(opts, collections.abc.Mapping):
            opts = {}
        num_traces = Plot.get_num_traces(x, y=y, source=source)

        # common trace options
        def get_default_trace_opts(trace: Any):
            return (
                dict(
                    filter(
                        lambda pair: False
                        if pair[0]
                        in {"name", "values", "tags", "matplotlib", "bokeh", "plotly"}
                        else True,
                        trace.items(),
                    )
                )
                if isinstance(trace, collections.abc.Mapping)
                else {}
            )

        def get_trace_color(trace: Any, default: str = None):
            return trace.get("color", None) or default

        def get_trace_mode(trace: Any, default: str = None):
            # lines, markers, text
            return trace.get("mode", None) or default

        # maplotlib and seaborn
        if plot_with in {"matplotlib", "seaborn"}:
            # see, https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html

            def get_plot_opts(options: Dict) -> Dict:
                return (
                    options.get("matplotlib", {})
                    if isinstance(options, collections.abc.Mapping)
                    else {}
                )

            def get_trace_opts(trace: Any) -> Dict:
                return (
                    trace.get("matplotlib", {})
                    if isinstance(trace, collections.abc.Mapping)
                    else {}
                )

            def get_trace_marker_symbol(trace_opts: Any, default: str = None) -> str:
                return trace_opts.get("marker", "") or default

            # default options
            plot_opts = get_plot_opts(opts)
            is_seaborn = plot_with == "seaborn"
            step_plots = {"step"}
            default_line_mode = "lines+markers"
            default_marker_symbol = "."

            # figure and axes
            if not figure:
                fig, ax = plt.subplots()
            else:
                fig = figure[0]
                axes = figure[1]
                if getattr(axes, "ndim", 0) == 0:
                    ax = axes
                elif axes.ndim == 1:
                    ax = axes[max((row or 1) - 1, (col or 1) - 1)]
                else:
                    ax = axes[(row or 1) - 1, (col or 1) - 1]
            if is_seaborn:
                # set seaborn styling
                sns.set()

            def add_trace(ax, x_trace, y_trace):
                x_values = Plot.get_trace_values(x_trace)
                y_values = Plot.get_trace_values(y_trace)
                trace_name = Plot.get_trace_name(y_trace, default="")
                trace_opts = get_trace_opts(y_trace)
                default_trace_opts = get_default_trace_opts(y_trace)
                trace_color = get_trace_color(
                    trace_opts,
                    default=get_trace_color(
                        default_trace_opts, default=get_trace_color(plot_opts)
                    ),
                )
                trace_mode = get_trace_mode(
                    trace_opts,
                    default=get_trace_mode(
                        default_trace_opts,
                        default=default_line_mode,
                    ),
                )
                trace_marker_symbol = get_trace_marker_symbol(
                    trace_opts,
                    default=get_trace_marker_symbol(
                        default_trace_opts,
                        default=default_marker_symbol,
                    ),
                )
                try:
                    if "markers" in trace_mode and "lines" not in trace_mode:
                        trace = ax.scatter(x_values, y_values, label=trace_name)
                    else:
                        if chart_type in step_plots:
                            (trace,) = ax.step(x_values, y_values, label=trace_name)
                        else:
                            (trace,) = ax.plot(x_values, y_values, label=trace_name)
                    # set trace properties
                    if trace:
                        if trace_color and hasattr(trace, "set_color"):
                            trace.set_color(trace_color)
                        if "markers" in trace_mode and hasattr(trace, "set_marker"):
                            trace.set_marker(trace_marker_symbol)

                except Exception as ex:
                    print(
                        f"Error occurred while plotting: Plot='{title}', Trace='{trace_name}'"
                    )
                    print(ex)

            if num_traces > 1:
                for idx in range(num_traces):
                    add_trace(ax, *Plot.get_trace(x, y, idx))
                # ax.legend()
            elif num_traces > 0:
                add_trace(ax, *Plot.get_trace(x, y))

            if num_traces > 0:
                ax.set_title(title)
                if xaxis_title:
                    ax.set_xlabel(xaxis_title)
                if yaxis_title:
                    ax.set_ylabel(yaxis_title)
                if xaxis_range:
                    ax.set_xlim(xaxis_range)
                if yaxis_range:
                    ax.set_ylim(yaxis_range)
                if xaxis_type == "log":
                    ax.set_xscale("log")
                if yaxis_type == "log":
                    ax.set_yscale("log")
                ax.minorticks_on()
                if show_grid:
                    ax.grid()

            if show or image_file:
                plt.tight_layout()
                # width and height, default (6.4, 4.8) inch - plt.figurercParams["figure.figsize"]
                if width:
                    px_to_inch = (
                        1 / plt.rcParams["figure.dpi"]
                    )  # pixel in inches, typically 100 pixels per inch
                    fig.set_figwidth(width * px_to_inch)
                if height:
                    px_to_inch = (
                        1 / plt.rcParams["figure.dpi"]
                    )  # pixel in inches, typically 100 pixels per inch
                    fig.set_figheight(height * px_to_inch)

            if image_file:
                plt.savefig(image_file)
            if show:
                try:
                    plt.show()
                except Exception as ex:
                    print(ex)
            return fig

        # bokeh
        elif plot_with == "bokeh":

            def get_plot_opts(options: Any) -> Dict:
                return (
                    options.get("bokeh", {})
                    if isinstance(options, collections.abc.Mapping)
                    else {}
                )

            def get_trace_opts(trace: Any) -> Dict:
                return (
                    trace.get("bokeh", {})
                    if isinstance(trace, collections.abc.Mapping)
                    else {}
                )

            def get_trace_fill_color(trace_opts: Dict, default: str = None):
                return trace_opts.get("fill_color", None) or default

            def get_trace_line_color(trace_opts: Dict, default: str = None):
                return trace_opts.get("line_color", None) or default

            # default options
            plot_opts = get_plot_opts(opts)
            step_plots = {"step"}
            default_line_mode = "lines+markers"

            # figure
            fig = (
                bh.figure(
                    x_axis_type=xaxis_type or "linear",
                    y_axis_type=yaxis_type or "linear",
                )
                if not figure
                else figure
            )
            if row and col:
                fig[row - 1][col - 1] = bh.figure(
                    x_axis_type=xaxis_type or "linear",
                    y_axis_type=yaxis_type or "linear",
                )
                ax = fig[row - 1][col - 1]
            else:
                ax = fig if not isinstance(fig, list) else None
            fig_layout = None

            def add_trace(ax, x_trace, y_trace):
                x_values = Plot.get_trace_values(x_trace)
                y_values = Plot.get_trace_values(y_trace)
                trace_name = Plot.get_trace_name(y_trace, default="")
                trace_opts = get_trace_opts(y_trace)
                default_trace_opts = get_default_trace_opts(y_trace)
                trace_color = get_trace_color(
                    trace_opts,
                    default=get_trace_color(
                        default_trace_opts, default=get_trace_color(plot_opts)
                    ),
                )
                trace_fill_color = get_trace_fill_color(
                    trace_opts, default=get_trace_fill_color(plot_opts)
                )
                trace_line_color = get_trace_fill_color(
                    trace_opts, default=get_trace_line_color(plot_opts)
                )
                trace_mode = get_trace_mode(
                    trace_opts,
                    default=get_trace_mode(
                        default_trace_opts, default=default_line_mode
                    ),
                )
                glyph_name = trace_name or "glyph"
                marker_glyph_name = f"{glyph_name}_marker"
                try:
                    renderers = {}
                    if "markers" in trace_mode:
                        renderers["marker"] = ax.scatter(
                            x_values,
                            y_values,
                            name=marker_glyph_name,
                            legend_label=trace_name,
                        )
                    if "lines" in trace_mode:
                        if chart_type in step_plots:
                            renderers["line"] = ax.step(
                                x_values,
                                y_values,
                                name=glyph_name,
                                legend_label=trace_name,
                            )
                        else:
                            renderers["line"] = ax.line(
                                x_values,
                                y_values,
                                name=glyph_name,
                                legend_label=trace_name,
                            )

                    if renderers:
                        # legend name
                        ax.legend.items[-1].visible = True if trace_name else False

                        # select glyph
                        # NOTE: the order of selection is inverse to the order in which glyphs were added
                        for trace_type, renderer in renderers.items():
                            trace = renderer.glyph
                            # set trace properties
                            if trace:
                                if trace_color:
                                    if hasattr(trace, "fill_color"):
                                        trace.fill_color = trace_color
                                    if hasattr(trace, "line_color"):
                                        trace.line_color = trace_color
                                if trace_fill_color and hasattr(trace, "fill_color"):
                                    trace.fill_color = trace_fill_color
                                if trace_line_color and hasattr(trace, "line_color"):
                                    trace.line_color = trace_line_color
                except Exception as ex:
                    print(
                        f"Error occurred while plotting: Plot='{title}', Trace='{trace_name}'"
                    )
                    print(ex)

            if num_traces > 1:
                for idx in range(num_traces):
                    add_trace(ax, *Plot.get_trace(x, y, idx))
            elif num_traces > 0:
                add_trace(ax, *Plot.get_trace(x, y))

            # subplot axes and layout
            if ax:
                ax.title.text = title or ""
                ax.xaxis.axis_label = xaxis_title or ""
                ax.yaxis.axis_label = yaxis_title or ""

            if row and col:
                pass

            if show or image_file:
                if isinstance(fig, list):
                    fig_layout = bh_layouts.gridplot(fig)
                    # layout title
                    if title:
                        layout_title = bh_models.Div(text=title, align="center")
                        fig_layout = bh_layouts.column(layout_title, fig_layout)
                    # width and height, default (600, 600)
                    if width:
                        fig_layout.plot_width = width
                    if height:
                        fig_layout.plot_height = height
                else:
                    # width and height, default (600, 600)
                    if width:
                        fig.plot_width = width
                    if height:
                        fig.plot_height = height

            if show:
                try:
                    Plot.init_bokeh()
                    if fig_layout:
                        bh.show(fig_layout)
                    elif not isinstance(fig, list):
                        bh.show(fig)
                except Exception as ex:
                    print(ex)

            return fig

        # plotly
        else:
            # see, https://plotly.com/python/subplots/
            # see, https://plotly.com/python/axes/
            # see, https://plotly.com/python/log-plot/
            # see, https://plotly.com/python/line-charts/
            # see, https://plotly.com/python/figure-labels/
            # see, https://plotly.com/python/marker-style/

            def get_plot_opts(options: Any) -> Dict:
                return (
                    options.get("plotly", {})
                    if isinstance(options, collections.abc.Mapping)
                    else {}
                )

            def get_trace_opts(trace: Any) -> Dict:
                return (
                    trace.get("plotly", {})
                    if isinstance(trace, collections.abc.Mapping)
                    else {}
                )

            def update_trace_opts(trace_opts: Any, prop_name: str, default: str = None):
                trace_prop = (
                    trace_opts.get(prop_name, None)
                    if isinstance(trace_opts, collections.abc.Mapping)
                    else None
                )
                trace_prop = trace_prop or default
                if trace_prop:
                    if not isinstance(trace_opts, collections.abc.Mapping):
                        trace_opts = {}
                    trace_opts.update({prop_name: trace_prop})
                return trace_opts

            def get_trace_marker(trace_opts: Dict, default: Dict = None):
                return trace_opts.get("marker", None) or default

            def get_trace_line(trace_opts: Dict, default: str = None):
                return trace_opts.get("line", None) or default

            def update_trace_line_color(trace_line: Any, default: str = None):
                return update_trace_opts(trace_line, prop_name="color", default=default)

            def update_trace_line_shape(trace_line: Any, default: str = None):
                shapes = {"hv", "vh", "hvh", "vhv", "spline", "linear"}
                return update_trace_opts(trace_line, prop_name="shape", default=default)

            def update_trace_line_dash(trace_line: Any, default: str = None):
                dashes = {"solid", "dot", "dash", "longdash", "dashdot", "longdashdot"}
                return update_trace_opts(trace_line, prop_name="dash", default=default)

            # default options
            plot_opts = get_plot_opts(opts)
            step_plots = {"step"}
            default_line_mode = "lines+markers"
            default_line_shape = "hv" if chart_type in step_plots else "linear"

            # figure
            fig = go.Figure() if not figure else figure

            def add_trace(ax, x_trace, y_trace):
                x_values = Plot.get_trace_values(x_trace)
                y_values = Plot.get_trace_values(y_trace)
                trace_name = Plot.get_trace_name(y_trace, default="")
                trace_opts = get_trace_opts(y_trace)
                default_trace_opts = get_default_trace_opts(y_trace)
                trace_color = get_trace_color(
                    trace_opts,
                    default=get_trace_color(
                        default_trace_opts, default=get_trace_color(plot_opts)
                    ),
                )
                trace_line = get_trace_line(
                    trace_opts, default=get_trace_line(plot_opts)
                )
                trace_line = update_trace_line_shape(
                    trace_line, default=default_line_shape
                )
                trace_line = update_trace_line_color(trace_line, default=trace_color)
                trace_marker = get_trace_marker(
                    trace_opts, default=get_trace_marker(plot_opts)
                )
                trace_mode = get_trace_mode(
                    trace_opts,
                    default=get_trace_mode(
                        default_trace_opts,
                        default=default_line_mode,
                    ),
                )
                try:
                    ax.add_trace(
                        go.Scatter(
                            x=x_values,
                            y=y_values,
                            mode=trace_mode,
                            name=trace_name,
                            line=trace_line,
                            marker=trace_marker,
                        ),
                        row=row,
                        col=col,
                    )
                except Exception as ex:
                    print(
                        f"Error occurred while plotting: Plot='{title}', Trace='{trace_name}'"
                    )
                    print(ex)

            if num_traces > 1:
                for idx in range(num_traces):
                    add_trace(fig, *Plot.get_trace(x, y, idx))
            elif num_traces > 0:
                add_trace(fig, *Plot.get_trace(x, y))

            # axis title
            if xaxis_title:
                fig.update_xaxes(
                    title_text=xaxis_title,
                    row=row,
                    col=col,
                )
            if yaxis_title:
                fig.update_yaxes(
                    title_text=yaxis_title,
                    row=row,
                    col=col,
                )

            # axis range
            if xaxis_range:
                fig.update_xaxes(
                    range=xaxis_range,
                    constrain="domain",
                    row=row,
                    col=col,
                )
            if yaxis_range:
                fig.update_yaxes(
                    range=yaxis_range,
                    constrain="domain",
                    row=row,
                    col=col,
                )

            # axis type: 'linear', 'log', etc.
            if xaxis_type:
                fig.update_xaxes(
                    type=xaxis_type,
                    row=row,
                    col=col,
                )
            if yaxis_type:
                fig.update_yaxes(
                    type=yaxis_type,
                    row=row,
                    col=col,
                )

            # show grid
            fig.update_xaxes(
                showgrid=show_grid,
                row=row,
                col=col,
            )
            fig.update_yaxes(
                showgrid=show_grid,
                row=row,
                col=col,
            )

            # subplot axes and layout
            if row and col:
                # subplot index
                rows, cols = fig._get_subplot_rows_columns()
                subplot_idx = (row - 1) * len(cols) + (col - 1)

                # subplot title
                fig.layout.annotations[subplot_idx].update(text=title or "")

            # layout
            if show or image_file:
                # figure width and height
                if width:
                    fig.update_layout(
                        width=width,
                    )
                if height:
                    fig.update_layout(
                        height=height,
                    )
                fig.update_layout(
                    title={
                        "text": title,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                    },
                    legend_title=legend_title,
                )
            # save figure
            if image_file:
                try:
                    fig.write_image(image_file)
                except Exception as ex:
                    print(ex)
            # show plot
            if show:
                try:
                    fig.show()
                except Exception as ex:
                    print(ex)
            return fig

    @staticmethod
    def animate_solution(
        t,
        x: Union[Tuple, List[Tuple], Any],
        y: Optional[Any] = None,
        title: str = None,
        xaxis_title: str = None,
        yaxis_title: str = None,
        xaxis_range: Union[Tuple, List] = None,
        yaxis_range: Union[Tuple, List] = None,
        source: Union[Dict, pd.DataFrame] = None,
        width: int = None,
        height: int = None,
        plot_with: str = "plotly",
        **kwargs,
    ):
        """
        Plot data using one of the libraries, such as plotly(default), bokeh, matplotlib/seaborn.

        Parameters
        __________
        t :  tuple, list, array-like
            Time
        x : tuple, list, array-like
            List of traces [(x1,y1), (x2,y2)] or single trace (x,y) or x array-like
        y : array-like or None
            y array-like
        source : dict, DataFrame, default None
            Data source, which allows to refer to x and y by DataFrame column or dictionary field name
        width : int, default None
            Plot width
        height : int, default None
            Plot height
        title : str, default ''
            Plot title
        xaxis_title : str, default None
            X axis title
        yaxis_title : str, default None
            Y axis title
        xaxis_range : tuple, list
            X axis range
        yaxis_range : tuple, list
            Y axis range
        plot_with : str, default 'plotly'
            Plot library, one of 'matplotlib', 'seaborn', 'plotly', 'bokeh'
        """

        num_frames = len(t)
        num_traces = Plot.get_num_traces(x, y=y, source=source)

        def get_trace_color(trace: Any, default: str = None):
            return trace.get("color", None) or default

        # plot specs
        height = height or 600
        width = width or None

        # Plot.get_trace(x, y, idx)
        # x_values = Plot.get_trace_values(x_trace)
        # y_values = Plot.get_trace_values(y_trace)
        # trace_name = Plot.get_trace_name(y_trace, default="")
        time_display_precision = 4
        get_x = lambda x_trace, _: Plot.get_trace_values(x_trace)
        get_y = lambda y_trace, i: Plot.get_trace_values(y_trace[i])
        get_time = lambda i: t[i]
        get_time_label = lambda i: round(t[i], time_display_precision)

        # Plot results
        if plot_with in {"matplotlib", "seaborn"}:
            is_seaborn = plot_with == "seaborn"

            fig, ax = plt.subplots()
            if is_seaborn:
                # set seaborn styling
                sns.set()

            # Turn interactive plotting off
            plt.rcParams["animation.html"] = "jshtml"
            plt.rcParams["figure.dpi"] = 150
            px_to_inch = 1 / plt.rcParams["figure.dpi"]

            # Initial conditions
            trace_plot = [None for _ in range(num_traces)]
            for idx in range(num_traces):
                x_trace, y_trace = Plot.get_trace(x, y, idx)
                x_values = get_x(x_trace, 0)
                y_values = get_y(y_trace, 0)
                trace_name = Plot.get_trace_name(y_trace, default="")
                (trace_plot[idx],) = plt.plot(
                    x_values, y_values, color="red", label=trace_name
                )

            plt.title(title)
            if height:
                fig.set_figheight(height * px_to_inch)
            if width:
                fig.set_figwidth(width * px_to_inch)

            ax.set(
                xlabel=xaxis_title,
                ylabel=yaxis_title,
            )
            if xaxis_range:
                ax.set_xlim(xaxis_range)
            if yaxis_range:
                ax.set_ylim(yaxis_range)
            ax.legend()

            def update(i):
                for idx in range(num_traces):
                    x_trace, y_trace = Plot.get_trace(x, y, idx)
                    # x_values = get_x(x_trace, i)
                    y_values = get_y(y_trace, i)
                    # trace_plot[idx].set_xdata(x_values)
                    trace_plot[idx].set_ydata(y_values)
                return tuple(trace_plot)

            # plt.show()
            # plt.close()
            return animation.FuncAnimation(
                fig=fig, func=update, frames=num_frames, interval=30
            )

        elif plot_with in {"bokeh"}:
            frames = dict(traces=[])
            for idx in range(num_traces):
                x_trace, y_trace = Plot.get_trace(x, y, idx)
                x_values = get_x(x_trace, 0)
                y_values = get_y(y_trace, 0)
                trace_name = Plot.get_trace_name(y_trace, default="")
                frames["traces"].append(
                    dict(
                        x=x_trace,
                        y=y_trace.tolist()
                        if isinstance(y_trace, np.ndarray)
                        else y_trace,
                    )
                )

            sources = []
            for idx in range(num_traces):
                x_trace, y_trace = Plot.get_trace(x, y, idx)
                x_values = get_x(x_trace, 0)
                y_values = get_y(y_trace, 0)
                trace_name = Plot.get_trace_name(y_trace, default="")
                sources.append(
                    bh_models.ColumnDataSource(data=dict(x=x_values, y=y_values)),
                )

            plot = bh.figure(
                title=title,
                width=width or 600,
                height=height or 800,
            )
            if xaxis_range:
                plot.x_range = bh_models.Range1d(*xaxis_range)
            if yaxis_range:
                plot.y_range = bh_models.Range1d(*yaxis_range)
            plot.title.align = "center"
            plot.xaxis.axis_label = xaxis_title or ""
            plot.yaxis.axis_label = yaxis_title or ""
            for idx in range(num_traces):
                x_trace, y_trace = Plot.get_trace(x, y, idx)
                trace_name = Plot.get_trace_name(y_trace, default="")
                plot.line(
                    x="x",
                    y="y",
                    source=sources[idx],
                    line_width=3,
                    line_alpha=0.6,
                    color="blue",
                    legend_label=trace_name,
                )
                plot.legend.items[-1].visible = True if trace_name else False

            time_slider = bh_models.Slider(
                start=0,
                end=num_frames - 1,
                value=0,
                step=1,
                title="Time",
                align="center",
            )
            callback = bh_models.CustomJS(
                args=dict(sources=sources, frames=frames, time_slider=time_slider),
                code="""
                const idx = time_slider.value;
                const traces = frames.traces;
                for (let i = 0; i < sources.length; i++) {
                    const x = sources[i].data.x;
                    const y = traces[i].y[idx];
                    sources[i].data = { x, y };
                }
            """,
            )
            time_slider.js_on_change("value", callback)

            Plot.init_bokeh()
            bh.show(bh_layouts.column(plot, time_slider))

        elif plot_with in {"plotly"}:
            frame_duration = 50  # time between frames
            transition_duration = 0  # line transition animation time

            def get_plots(i):
                trace_plot = []
                for idx in range(num_traces):
                    x_trace, y_trace = Plot.get_trace(x, y, idx)
                    x_values = get_x(x_trace, i)
                    y_values = get_y(y_trace, i)
                    trace_name = Plot.get_trace_name(y_trace, default="")
                    trace_plot.append(
                        {
                            "x": x_values,
                            "y": y_values,
                            "mode": "lines",
                            "text": f"frame[{i}]",
                            "name": trace_name,
                            "fillcolor": "red",
                        }
                    )
                return tuple(trace_plot)

            # make figure
            fig_dict = {"data": [], "layout": {}, "frames": []}

            # fill in most of layout
            fig_dict["layout"]["xaxis"] = {
                "title": xaxis_title,
            }
            if xaxis_range:
                fig_dict["layout"]["xaxis"]["range"] = xaxis_range
            fig_dict["layout"]["yaxis"] = {
                "title": yaxis_title,
            }
            if yaxis_range:
                fig_dict["layout"]["yaxis"]["range"] = yaxis_range
            fig_dict["layout"]["title"] = {"text": title, "x": 0.5}
            if height:
                fig_dict["layout"]["height"] = height
            if width:
                fig_dict["layout"]["height"] = width

            fig_dict["layout"]["hovermode"] = "closest"
            fig_dict["layout"]["updatemenus"] = [
                {
                    "buttons": [
                        {
                            "args": [
                                None,
                                {
                                    "frame": {
                                        "duration": frame_duration,
                                        "redraw": False,
                                    },
                                    "fromcurrent": True,
                                    "transition": {
                                        "duration": transition_duration,
                                        "easing": "quadratic-in-out",
                                    },
                                },
                            ],
                            "label": "Play",
                            "method": "animate",
                        },
                        {
                            "args": [
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0},
                                },
                            ],
                            "label": "Pause",
                            "method": "animate",
                        },
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top",
                }
            ]

            sliders_dict = {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Time:",
                    "visible": True,
                    "xanchor": "right",
                },
                "transition": {
                    "duration": transition_duration,
                    "easing": "cubic-in-out",
                },
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [],
            }

            # add plots
            fig_dict["data"].extend(get_plots(0))

            # make frames
            for i in range(0, num_frames):
                frame_name = str(get_time(i))
                frame = {
                    "data": [],
                    "name": frame_name,
                }
                # add plots
                frame["data"].extend(get_plots(i))
                # add frame
                fig_dict["frames"].append(frame)
                slider_step = {
                    "args": [
                        [frame_name],
                        {
                            "frame": {"duration": frame_duration, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": transition_duration},
                        },
                    ],
                    "label": get_time_label(i),
                    "method": "animate",
                }
                sliders_dict["steps"].append(slider_step)

            fig_dict["layout"]["sliders"] = [sliders_dict]

            fig = go.Figure(fig_dict)

            fig.show()

    @staticmethod
    def init_bokeh():
        if BokehInit.instance is None:
            BokehInit.instance = BokehInit()
        return BokehInit.instance


class BokehInit:
    instance = None

    def __init__(self):
        bh_io.output_notebook()
