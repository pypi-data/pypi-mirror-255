"""Plot routines"""


import copy
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import matplotlib.cm
import matplotlib.figure
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from IPython.display import Markdown, display
from matplotlib import ticker
from matplotlib.collections import PolyCollection
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from roxieapi.commons import roxie_style
from roxieapi.commons.roxie_constants import PlotLabels
from roxieapi.commons.types import (
    Base3DGeometry,
    CoilGeometry,
    Geometry,
    GraphPlot,
    HarmonicCoil,
    Plot2D,
    Plot3D,
    PlotInfo,
    PlotLegend,
)
from roxieapi.input.builder import RoxieInputBuilder
from roxieapi.output.parser import RoxieOutputParser

try:
    import pyvista as pv
except ImportError:
    _has_pyvista = False
else:
    _has_pyvista = True


def requires_pv(func):
    def inner(*arg):
        if _has_pyvista:
            return func(*arg)
        else:
            print("Missing dependency to pyvista")

    return inner


class RoxieGraphsPlotly:
    """Roxie Graph output
    A class for plotting Standard graph plots from a roxie output
    """

    def __init__(self, output_parser: RoxieOutputParser):
        """Initialize RoxieGraphs with an output parser

        :param output_parser: the parser to use for all graphs
        """
        self.output_parser = output_parser

    def plot_device_graph(
        self,
        graphPlot: GraphPlot,
        opt_step: int = 1,
        trans_step: int = 1,
        fig_size: Optional[Tuple[float, float]] = None,
    ) -> Optional[go.Figure]:
        """Plot a device graph
        :param graphPlot: The GraphPlot object from the RoxieOutputParser
        :param opt_step: Optimization step
        :param trans_step: Transient step
        :param fig_size: Size of the figure (in inch), defaults to None
        :return: a plotly graph_objs.Figure object, or None if Plot data is missing
        """
        if step := self.output_parser.find_transstep(opt_step, trans_step):
            return self.plot_graph(graphPlot, step.deviceGraphs, fig_size)
        return None

    def plot_transient_graph(
        self,
        graphPlot: GraphPlot,
        opt_step: int = 1,
        fig_size: Optional[Tuple[float, float]] = None,
    ) -> Optional[go.Figure]:
        """Plot a device graph
        :param graphPlot: The GraphPlot object from the RoxieOutputParser
        :param opt_step: Optimization step
        :param fig_size: Size of the figure (in inch), defaults to None
        :return: a plotly graph_objs.Figure object, or None if Plot data is missing
        """
        if opt := self.output_parser.find_optstep(opt_step):
            return self.plot_graph(graphPlot, opt.transientGraphs, fig_size)
        return None

    def plot_optimization_graph(
        self,
        graphPlot: GraphPlot,
        fig_size: Optional[Tuple[float, float]] = None,
    ) -> Optional[go.Figure]:
        """Plot a device graph
        :param graphPlot: The GraphPlot object from the RoxieOutputParser
        :param fig_size: Size of the figure (in inch), defaults to None
        :return: a plotly graph_objs.Figure object, or None if Plot data is missing
        """
        return self.plot_graph(
            graphPlot, self.output_parser.optimizationGraphs, fig_size
        )

    @staticmethod
    def plot_graph(
        graphPlot: GraphPlot,
        data: Dict[int, pd.DataFrame],
        fig_size: Optional[Tuple[float, float]] = None,
    ) -> Optional[go.Figure]:
        """Plot a graph
        :param graphPlot: The GraphPlot object from the RoxieOutputParser
        :param data: Corresponding data object from the ROxieOutputParser
        :param fig_size: Size of the figure (in inch), defaults to None
        :return: a plotly graph_objs.Figure object, or None if Plot data is missing
        """
        title = graphPlot.title
        axisX = graphPlot.axes["X"]
        axisY = graphPlot.axes["Y"]

        if graphPlot.graphs[0].id not in data:
            return None

        p = graphPlot.graphs[0]
        fig = go.Figure()
        if fig_size:
            px_size = plt.rcParams["figure.dpi"]  # pixel in inches
            fig.update_layout(
                autosize=False,
                width=fig_size[0] * px_size,
                height=fig_size[1] * px_size,
            )

        fig.update_layout(title=title, showlegend=True)
        fig.update_xaxes(title=axisX.label, range=axisX.bounds)
        fig.update_yaxes(title=axisY.label, range=axisY.bounds)
        if axisX.log:
            fig.update_xaxes(type="log")
        if axisY.log:
            fig.update_yaxes(type="log")

        for p in graphPlot.graphs:
            lbl = p.label if p.label else f"Graph {p.id}"
            fig.add_trace(go.Scatter(x=data[p.id]["x"], y=data[p.id]["y"], name=lbl))
        return fig

    @staticmethod
    def plot_forces(
        data: pd.DataFrame,
        fig_size: Optional[Tuple[float, float]] = None,
    ) -> go.Figure:
        """Plot The Forces on conductor (plot similar to roxie plot in pdf)
        :param data: The dataframe with the forces defined (from RoxieOutputParser)
        :param fig_size: Size of the figure in inches, defaults to None
        :return: the figure
        """
        fig = go.Figure()
        fig.update_layout(
            title="Lorenz Forces in Conductor",
            xaxis_title="Conductor Nr",
            yaxis_title="Force in N/m",
        )
        if fig_size:
            px_size = plt.rcParams["figure.dpi"]  # pixel in inches
            fig.update_layout(
                autosize=False,
                width=fig_size[0] * px_size,
                height=fig_size[1] * px_size,
            )

        cols = [
            ("fx", "X component"),
            ("fy", "Y component"),
            ("ftr", "Perpendicular"),
            ("fpa", "Parallel"),
            ("fra", "Radial"),
            ("faz", "Azimuthal"),
        ]

        for c, n in cols:
            fig.add_trace(go.Scatter(x=data["cond"], y=data[c], mode="markers", name=n))
        return fig

    @staticmethod
    def plot_harmonics(
        coil: HarmonicCoil,
        fig_size: Optional[Tuple[float, float]] = None,
    ) -> go.Figure:
        """Plot the Harmonics as a bar graph
        :param coil: The coil to plot the harmonics for
        :param fig_size: Size of figure, in inches, defaults to None
        :return: The figure
        """
        bnvals = list(coil.bn.values())
        anvals = list(coil.an.values())
        if not coil.absolute:
            if coil.skew:
                anvals[coil.order - 1] = 0
            else:
                bnvals[coil.order - 1] = 0

        fig = go.Figure(
            data=[
                go.Bar(
                    name="Bn" if coil.absolute else "bn",
                    x=list(coil.bn.keys()),
                    y=bnvals,
                ),
                go.Bar(
                    name="An" if coil.absolute else "an",
                    x=list(coil.an.keys()),
                    y=anvals,
                ),
            ]
        )
        fig.update_layout(
            title=f"Harmonic coil {coil.id}",
            xaxis_title="Order",
            yaxis_title=f"Multipole in {'T' if coil.absolute else 'units'}",
            barmode="group",
        )
        if fig_size:
            px_size = plt.rcParams["figure.dpi"]  # pixel in inches
            fig.update_layout(
                autosize=False,
                width=fig_size[0] * px_size,
                height=fig_size[1] * px_size,
            )

        return fig


class RoxiePlots2D:
    """2D Plots for roxie (geometry + data)"""

    @dataclass
    class CBarInfo:
        pos: str = "w"
        lbls: List[str] = field(default_factory=list)
        vmin: Optional[float] = None
        vmax: Optional[float] = None
        objs: List[matplotlib.cm.ScalarMappable] = field(default_factory=list)

    def __init__(self, output_parser: RoxieOutputParser) -> None:
        """Create a new RoxiePlots2D object. Stores internally color maps, figures and axis"""
        self.roxie_pv = np.array(roxie_style.roxie_color_palette) / 256
        self.roxie_cm = ListedColormap(self.roxie_pv)  # type: ignore
        self.logger = logging.getLogger("RoxiePlots2D")
        self.mirrorX = False
        self.mirrorY = False
        self.output_parser = output_parser

    @staticmethod
    def _quads_to_tris(roxie_elements: List[List[int]]) -> list[list[int]]:
        """convert quads to tris
        :param quads: Quad input
        :return: tri output
        """
        # Check if there are already tris in the input
        nr_quads = sum(1 for x in roxie_elements if x[0] == 8)
        nr_tris = sum(1 for x in roxie_elements if x[0] == 6)
        if nr_quads + nr_tris < len(roxie_elements):
            raise Exception("Encountered Elements in input which are neither T6 nor Q8")

        tris = [[-1 for j in range(3)] for i in range(6 * nr_quads + 4 * nr_tris)]
        j = 0
        for i in range(len(roxie_elements)):
            if roxie_elements[i][0] == 8:
                n = [roxie_elements[i][k] for k in range(1, 9)]
                tris[j + 0] = [n[0], n[1], n[7]]
                tris[j + 1] = [n[2], n[3], n[1]]
                tris[j + 2] = [n[4], n[5], n[3]]
                tris[j + 3] = [n[6], n[7], n[5]]
                tris[j + 4] = [n[1], n[3], n[7]]
                tris[j + 5] = [n[5], n[7], n[3]]
                j += 6
            else:
                n = [roxie_elements[i][k] for k in range(1, 7)]
                tris[j + 0] = [n[0], n[1], n[5]]
                tris[j + 1] = [n[1], n[2], n[3]]
                tris[j + 2] = [n[3], n[4], n[5]]
                tris[j + 3] = [n[5], n[1], n[3]]
                j += 4

        return tris

    @staticmethod
    def _mirrorX(geom: Geometry) -> Geometry:
        """generate a mirror of geometry, mirrored over x axis
        :param geom: the geometry
        :return: mirrored geometry
        """
        geom_m = copy.deepcopy(geom)
        geom_m.nodes[:, 1] = -geom_m.nodes[:, 1]
        if geom.boundaries:
            for bound in geom.boundaries:
                assert geom_m.boundaries is not None
                geom_m.boundaries[bound][:, 0] = -geom.boundaries[bound][:, 0]
        return geom_m

    @staticmethod
    def _mirrorY(geom: Geometry) -> Geometry:
        """generate a mirror of geometry, mirrored over y axis
        :param geom: the geometry
        :return: mirrored geometry
        """
        geom_m = copy.deepcopy(geom)
        geom_m.nodes[:, 2] = -geom_m.nodes[:, 2]
        if geom.boundaries:
            for bound in geom.boundaries:
                assert geom_m.boundaries is not None
                geom_m.boundaries[bound][:, 1] = -geom.boundaries[bound][:, 1]
        return geom_m

    def _create_plot(self, plot: Plot2D, figsize: Tuple[int, int] = (15, 15)) -> None:
        """Create a plot and set defaults for axis, size and aspect ratio
        :param plot: the Plot2D description from roxie output
        :param figsize: size of the figure in inches, defaults to (15, 15)
        """
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, aspect="equal")

        self.cbars: Dict[str, RoxiePlots2D.CBarInfo] = {
            "w": RoxiePlots2D.CBarInfo(pos="w")
        }

        self.ax.set_title(plot.title)
        if plot.axes["X"].bounds:
            self.ax.set_xlim(
                left=plot.axes["X"].bounds[0], right=plot.axes["X"].bounds[1]
            )
        if plot.axes["Y"].bounds:
            self.ax.set_ylim(
                bottom=plot.axes["Y"].bounds[0], top=plot.axes["Y"].bounds[1]
            )
        self.ax.set_xlabel(plot.axes["X"].label)
        self.ax.set_ylabel(plot.axes["Y"].label)

    def _update_cb(
        self,
        obj: Optional[matplotlib.cm.ScalarMappable],
        label: Optional[str],
        min_val: float,
        max_val: float,
        legend: Optional[PlotLegend],
        replace: bool = False,
    ) -> CBarInfo:
        """Update the range of the Colorbar
        :param label: Label of data to plot
        :param min_val: min
        :param max_val: max
        :param replace: replace current values instead of updating, defaults to False
        """
        cbar_name = legend.pos if legend and legend.pos else "w"
        if cbar_name not in self.cbars:
            self.cbars[cbar_name] = RoxiePlots2D.CBarInfo(pos=cbar_name[0:1])
        cbar = self.cbars[cbar_name]
        if legend and legend.min_val is not None:
            cbar.vmin = legend.min_val
        elif replace or not cbar.vmin:
            cbar.vmin = min_val
        else:
            cbar.vmin = min(cbar.vmin, min_val)
        if legend and legend.max_val is not None:
            cbar.vmax = legend.max_val
        elif replace or not cbar.vmax:
            cbar.vmax = max_val
        else:
            cbar.vmax = max(cbar.vmax, max_val)

        if label:
            cbar.lbls.append(label)
        if obj:
            cbar.objs.append(obj)
        return cbar

    def _create_colorbars(self) -> None:
        """Create a colorbar"""
        divider = make_axes_locatable(self.ax)
        for name, cbarInfo in self.cbars.items():
            if not cbarInfo.objs:
                continue
            pos = cbarInfo.pos

            div_pos = (
                "right"
                if pos == "e"
                else "left"
                if pos == "w"
                else "top"
                if pos == "n"
                else "bottom"
            )
            pad = 0.05
            if div_pos in ["left", "bottom"]:
                pad = 0.5
            cax = divider.append_axes(div_pos, size="5%", pad=pad)
            sm = plt.cm.ScalarMappable(  # type: ignore
                cmap=self.roxie_cm,
                norm=plt.Normalize(vmin=cbarInfo.vmin, vmax=cbarInfo.vmax),  # type: ignore
            )
            lbl_txt = "\n".join(cbarInfo.lbls)
            cbar = self.fig.colorbar(
                sm, cax, label=lbl_txt, ticklocation="auto", location=div_pos
            )
            tick_locator = ticker.LinearLocator(numticks=len(self.roxie_pv) + 1)
            cbar.locator = tick_locator
            if div_pos in ["top", "bottom"]:
                cbar.ax.tick_params(rotation=90)
            cbar.update_ticks()
            for obj in cbarInfo.objs:
                obj.set_clim(vmin=cbarInfo.vmin, vmax=cbarInfo.vmax)

    def _create_cable_collection(
        self, coilGeom: Dict[int, CoilGeometry]
    ) -> PolyCollection:
        patches = [copy.copy(cable.geometry) for cable in coilGeom.values()]
        return PolyCollection(patches)

    def _plot_cables(self, coilGeom: Dict[int, CoilGeometry]) -> None:
        """Plot the cables of the geometry
        :param coilGeom: The coil geometry from the parser
        :raises Exception: if no plot was created
        """
        if not self.ax:
            raise Exception(
                "No plot created yet, cannot add cables. Call create_plot before"
            )
        pc = self._create_cable_collection(coilGeom)
        pc.set_facecolor("none")
        pc.set_edgecolor("blue")

        self.ax.add_collection(pc)  # type:ignore

    def _plot_strands(
        self,
        plotInfo: PlotInfo,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> None:
        """Plot The strands of the geometry
        :param opt_step: Optimization step
        :param trans_step: Transient step
        :param plotInfo: the PlotInfo object
        """

        coilGeom = None
        coilData = None
        cLegend = None
        dataLabel = None
        coilVector = None
        if opt := self.output_parser.opt.get(opt_step, None):
            coilGeom = opt.coilGeometries
        if step := self.output_parser.find_transstep(opt_step, trans_step):
            if plotInfo.dataType == "scalar":
                if plotInfo.id in step.coilData.columns:
                    coilData = step.coilData[plotInfo.id]
                elif plotInfo.harmCoil in step.harmonicCoils:
                    hc = step.harmonicCoils[plotInfo.harmCoil]
                    if plotInfo.id in hc.strandData.columns:
                        coilData = hc.strandData[plotInfo.id]
                if coilData is not None:
                    dataLabel = PlotLabels.plot2D_desc.get(
                        plotInfo.id, f"Plot id {plotInfo.id}"
                    )
                    cLegend = plotInfo.plotLegend

            elif plotInfo.dataType == "vector" and plotInfo.vector_mappings is not None:
                df = step.coilData
                id_x = plotInfo.vector_mappings.get("x", -1)
                id_y = plotInfo.vector_mappings.get("y", -1)
                if id_x in df.columns and id_y in df.columns:
                    vx = df[id_x]
                    vy = df[id_y]
                    coilVector = [vx, vy]

        if coilGeom is None:
            return

        patches = []
        centers_x = []
        centers_y = []
        for cable in coilGeom.values():
            for (
                strand_idx,
                strand,
            ) in cable.strands.items():
                patches.append(strand)
                centers_x.append(np.mean(strand[:, 0]))
                centers_y.append(np.mean(strand[:, 1]))

        p_strands = PolyCollection(patches)
        if coilData is not None:
            p_strands.set_array(coilData)
            p_strands.set_cmap(self.roxie_cm)

            self._update_cb(
                p_strands, dataLabel, np.min(coilData), np.max(coilData), cLegend
            )
        else:
            p_strands.set_edgecolor("black")

        if coilVector is not None:
            self.ax.quiver(centers_x, centers_y, coilVector[0], coilVector[1])

            # self._update_cb_range(dataLabel,np.min(meshData), np.max(meshData))

        self.ax.add_collection(p_strands)  # type: ignore

    @staticmethod
    def _mirror_iron(
        meshGeom: Geometry, mirror_x: bool = False, mirror_y: bool = False
    ) -> List[Geometry]:
        """Mirror the iron of meshGeometry in x and y
        :param meshGeom: The base geometry
        :param mirror_x: Mirror in x, defaults to False
        :param mirror_y: Mirror in y, defaults to False
        :return: List of Geometries (original + all mirrors)
        """
        geoms = []
        geoms.append(meshGeom)
        if mirror_x:
            geoms_mx = []
            for geom in geoms:
                geoms_mx.append(RoxiePlots2D._mirrorX(geom))
            geoms.extend(geoms_mx)
        if mirror_y:
            geoms_my = []
            for geom in geoms:
                geoms_my.append(RoxiePlots2D._mirrorY(geom))
            geoms.extend(geoms_my)
        return geoms

    def _plot_iron_boundary(self, geoms: List[Geometry]) -> None:
        """Plot the Boundary of the mesh geometries
        :param geoms: The list of geometries
        """
        boundaries = []
        for meshGeom in geoms:
            if meshGeom.boundaries is None:
                continue
            for f, bound in meshGeom.boundaries.items():
                boundaries.append(bound)
        p = PolyCollection(
            boundaries, facecolors="none", edgecolors="black", linewidth=0.5
        )
        self.ax.add_collection(p)  # type: ignore

    def _plot_iron_mesh(self, geoms: List[Geometry]) -> None:
        """Plot the iron mesh
        :param geoms: List of geometries
        """
        mesh = []
        for meshGeom in geoms:
            elems = meshGeom.elements
            if elems is None:
                continue
            for idx, elem in enumerate(elems):
                nodes = meshGeom.nodes[elem[1:]]
                mesh.append(copy.copy(nodes[:, 1:]))
        p = PolyCollection(mesh, facecolors="none", edgecolors="black", linewidth=0.5)
        self.ax.add_collection(p)  # type: ignore

    def _plot_matrix(
        self,
        plotInfo: PlotInfo,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> None:
        """Plot Vector Matrix over 2d plot
        :param output_parser: The output parser
        :param plotInfo: Plot info object
        :param opt_step: Optimization step, defaults to 1
        :param trans_step: Transient step, defaults to 1
        """
        matrixData = None
        step = self.output_parser.find_transstep(opt_step, trans_step)
        if step:
            matrixData = step.matrixData
            if matrixData is None:
                return

            df = matrixData.copy()
            if plotInfo.plotLegend:
                uniform_length = not plotInfo.plotLegend.greyScale
                plot_colors = uniform_length
            else:
                plot_colors = False
                uniform_length = True

            if plot_colors or uniform_length:
                df["vc"] = np.sqrt(df["vx"] ** 2 + df["vy"] ** 2)
            if uniform_length:
                df["vx"] = df["vx"] / df["vc"]
                df["vy"] = df["vy"] / df["vc"]
            if plot_colors:
                quiver = self.ax.quiver(
                    df["x"], df["y"], df["vx"], df["vy"], df["vc"], cmap=self.roxie_cm
                )
                self._update_cb(
                    quiver,
                    "2D Vector Matrix",
                    min(df["vc"]),
                    max(df["vc"]),
                    plotInfo.plotLegend,
                )
            else:
                self.ax.quiver(df["x"], df["y"], df["vx"], df["vy"])

    def _plot_iron(
        self,
        meshPlots: List[PlotInfo],
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> None:
        """Plot all iron related plots (mesh, boundaries, scalar values)
        :param plotInfo: The plot info object
        :param opt_step: Optimization step, defaults to 1
        :param trans_step: Transient step, defaults to 1
        :raises Exception: for mesh types which are not implemented yet
        """

        meshGeometries: List[Geometry] = []
        if opt_step not in self.output_parser.opt or meshPlots is None:
            return
        opt = self.output_parser.opt[opt_step]
        val = opt.meshGeometries
        if val is None:
            return
        if self.mirrorX or self.mirrorY:
            meshGeometries = self._mirror_iron(val, self.mirrorX, self.mirrorY)
        else:
            meshGeometries = [val]

        for plotInfo in meshPlots:
            if plotInfo.dataType == "mesh":
                self._plot_iron_mesh(meshGeometries)
            elif plotInfo.dataType == "surface":
                self._plot_iron_boundary(meshGeometries)
            elif plotInfo.dataType == "scalar":
                if (
                    trans_step in opt.step
                    and plotInfo.id in opt.step[trans_step].meshData.columns
                ):
                    data = opt.step[trans_step].meshData[plotInfo.id]
                    dataLabel = PlotLabels.plotMesh2D_desc.get(
                        plotInfo.id, f"Meshplot id {plotInfo.id}"
                    )
                    cbar = self._update_cb(
                        None, dataLabel, np.min(data), np.max(data), plotInfo.plotLegend
                    )
                    for meshGeom in meshGeometries:
                        nodes_x = meshGeom.nodes[:, 1]
                        nodes_y = meshGeom.nodes[:, 2]
                        if meshGeom.elements is None:
                            continue
                        elems_tris = RoxiePlots2D._quads_to_tris(meshGeom.elements)
                        triangulation = tri.Triangulation(nodes_x, nodes_y, elems_tris)
                        tricont = self.ax.tricontourf(
                            triangulation, data, levels=19, cmap=self.roxie_cm
                        )
                        cbar.objs.append(tricont)

            elif plotInfo.dataType == "vector":
                if trans_step in opt.step and plotInfo.vector_mappings is not None:
                    df = opt.step[trans_step].meshData
                    id_x = plotInfo.vector_mappings.get("x", -1)
                    id_y = plotInfo.vector_mappings.get("y", -1)
                    if id_x in df.columns and id_y in df.columns:
                        nodes = np.concatenate(
                            [meshGeom.nodes for meshGeom in meshGeometries]
                        )
                        nodes_x = nodes[:, 1]
                        nodes_y = nodes[:, 2]
                        vx = df[id_x]
                        vy = df[id_y]
                        self.ax.quiver(nodes_x, nodes_y, vx, vy)
            else:
                raise Exception(
                    "Mesh datatype {0} not yet implemented".format(plotInfo.dataType)
                )

    def plot_xs(
        self,
        pl: Plot2D,
        opt_step: int = 1,
        trans_step: int = 1,
        figsize=(8, 8),
    ) -> matplotlib.figure.Figure:
        """Plots a crosssection plot from Roxie
        :param pl: the Plot2D object
        :param opt_step: Optimization step
        :param trans_step: Transient step
        :param figsize: size of the figure
        :return: the matplotlib figure object
        """
        self._create_plot(pl, figsize=figsize)

        opt = self.output_parser.find_optstep(opt_step)
        if opt is None:
            return self.fig

        self._plot_cables(opt.coilGeometries)

        for pp in pl.pointPlots:
            # do nothing for now
            pass
        for cp in pl.coilPlots:
            self._plot_strands(
                cp,
                opt_step,
                trans_step,
            )
        self._plot_iron(
            pl.meshPlots,
            opt_step,
            trans_step,
        )
        for mp in pl.matrixPlots:
            self._plot_matrix(
                mp,
                opt_step,
                trans_step,
            )
        for ip in pl.irisPlots:
            pass

        self._create_colorbars()
        self.fig.axes[0].autoscale_view()

        return self.fig

    def plot_conductor_forces(
        self,
        opt_step: int = 1,
        trans_step: int = 1,
        fig_size: Tuple[int, int] = (12, 8),
    ) -> Optional[matplotlib.figure.Figure]:
        """Generates a set of 2D crosssection plots with Forces overlay (one plot per force)
        :param output_parser: The output parser
        :param opt_step: optimization step, defaults to 1
        :param trans_step: transient step, defaults to 1
        :param fig_size: figure size in inches, defaults to (12, 8)
        :return: the matplotlib figure object, or None if no conductor forces are available
        """

        if opt := self.output_parser.find_optstep(opt_step):
            if trans := self.output_parser.find_transstep(opt_step, trans_step):
                pc_glob = self._create_cable_collection(opt.coilGeometries)
                cond_forces = trans.conductorForces
                if cond_forces is not None:
                    max_force = cond_forces[cond_forces.columns[1:]].abs().max().max()

                    cols = [
                        ("fx", "X component"),
                        ("ftr", "Perpendicular"),
                        ("fra", "Radial"),
                        ("fy", "Y component"),
                        ("fpa", "Parallel"),
                        ("faz", "Azimuthal"),
                    ]

                    self.fig, axs = plt.subplots(
                        2,
                        3,
                        sharex=True,
                        sharey=True,
                        squeeze=True,
                        subplot_kw={"aspect": "equal"},
                        figsize=fig_size,
                    )
                    self.fig.suptitle("Lorenz forces in conductors")

                    ax = None
                    pc = None
                    for i, ax in enumerate(axs.flat):
                        ax.set_title(cols[i][1])  # type: ignore
                        pc = copy.copy(pc_glob)
                        pc.set_array(cond_forces[cols[i][0]])
                        pc.set_clim(-max_force, max_force)
                        pc.set_cmap("RdBu")
                        ax.add_collection(pc, autolim=True)  # type: ignore
                        ax.autoscale_view()  # type: ignore

                    assert pc is not None and ax is not None
                    self.fig.subplots_adjust(right=0.8)
                    cbar_ax = self.fig.add_axes((0.82, 0.15, 0.02, 0.68))
                    cbar = self.fig.colorbar(pc, ax=ax, cax=cbar_ax)
                    cbar.set_label("Force in N/m")

                    return self.fig
        return None


class RoxiePlots3D:
    @requires_pv
    def __init__(self, output_parser: RoxieOutputParser):
        self.roxie_pv = np.array(roxie_style.roxie_color_palette) / 256
        self.roxie_cm = ListedColormap(self.roxie_pv, name="roxie_colors")  # type: ignore
        pv.set_plot_theme("document")  # type: ignore
        pv.global_theme.cmap = self.roxie_cm
        self.output_parser = output_parser

    @requires_pv
    def _set_perspective(self, pl: "pv.Plotter") -> None:
        pl.camera_position = "xy"
        pl.camera.azimuth += 45
        pl.camera.elevation += 35.264

    @requires_pv
    def _create_plot(self, fig_size: Tuple[float, float] = (10.0, 8.0)) -> "pv.Plotter":
        px_size = plt.rcParams["figure.dpi"]  # pixel in inches
        window_size_px = [int(fig_size[0] * px_size), int(fig_size[1] * px_size)]
        return pv.Plotter(window_size=window_size_px, lighting="three lights")

    @requires_pv
    def _create_structured_grid(self, geom: Base3DGeometry) -> "pv.StructuredGrid":
        nodes = geom.geometry.nodes.copy()
        L = len(nodes) // 4
        for i in range(L):
            sw = (2, 3)
            tmp = nodes[i * 4 + sw[0], :].copy()
            nodes[i * 4 + sw[0], :] = nodes[i * 4 + sw[1], :]
            nodes[i * 4 + sw[1], :] = tmp
            pass
        X = np.reshape(nodes[:, 0], (L, 2, 2))
        Y = np.reshape(nodes[:, 1], (L, 2, 2))
        Z = np.reshape(nodes[:, 2], (L, 2, 2))
        # Create and plot structured grid
        block3d_data = pv.StructuredGrid(X, Y, Z)
        return block3d_data

    @requires_pv
    def create_coil_geometries(self, opt_step: int = 1) -> "pv.MultiBlock":
        coils = pv.MultiBlock()
        if opt := self.output_parser.find_optstep(opt_step):
            for id, geom in opt.coilGeometries3D.items():
                coils[str(id)] = self._create_structured_grid(geom)
        return coils

    @requires_pv
    def create_brick_geometries(self, opt_step: int = 1) -> "pv.MultiBlock":
        bricks = pv.MultiBlock()
        if opt := self.output_parser.find_optstep(opt_step):
            for id, geom in opt.brickGeometries3D.items():
                bricks[str(id)] = self._create_structured_grid(geom)
        return bricks

    @requires_pv
    def create_endspacer_geometries(self, opt_step: int = 1) -> "pv.MultiBlock":
        wedges = pv.MultiBlock()
        if opt := self.output_parser.find_optstep(opt_step):
            if wedgeGeom := opt.wedgeGeometries3D:
                for id, wedge in wedgeGeom.items():
                    edges = []

                    if wedge.inner_surface is None:
                        if wedge.outer_surface is not None:
                            edge_low = wedge.outer_surface.lower_edge.copy()
                            edge_up = wedge.outer_surface.upper_edge.copy()
                            edge_low[:, 2] = 0.0
                            edge_up[:, 2] = 0.0
                            edges.append(edge_low)
                            edges.append(edge_up)
                    else:
                        edges.append(wedge.inner_surface.lower_edge)
                        edges.append(wedge.inner_surface.upper_edge)
                    if wedge.outer_surface is None:
                        if wedge.inner_surface is not None:
                            edge_low = wedge.inner_surface.lower_edge.copy()
                            edge_up = wedge.inner_surface.upper_edge.copy()
                            max_z = max(edge_low[-1, 2], edge_up[-1, 2])
                            max_z = np.sign(max_z) * (abs(max_z) + 20)
                            edge_low[:, 2] = max_z
                            edge_up[:, 2] = max_z

                            edges.append(edge_low)
                            edges.append(edge_up)
                    else:
                        edges.append(wedge.outer_surface.lower_edge)
                        edges.append(wedge.outer_surface.upper_edge)

                    nodes = np.vstack([x for t in zip(*edges) for x in t])
                    L = len(nodes) // 4

                    X = np.reshape(nodes[:, 0], (L, 2, 2))
                    Y = np.reshape(nodes[:, 1], (L, 2, 2))
                    Z = np.reshape(nodes[:, 2], (L, 2, 2))
                    # Create and plot structured grid
                    mesh = pv.StructuredGrid(X, Y, Z)

                    wedges[f"l_{wedge.layer}_w{wedge.nr:02d}"] = mesh

        return wedges

    @requires_pv
    def get_endspacer_geometry(
        self,
        pl: Plot3D,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> "pv.MultiBlock":
        opt = self.output_parser.find_optstep(opt_step)
        if not opt or not opt.wedgeGeometries3D:
            return pv.MultiBlock()
        return self.create_endspacer_geometries(opt_step)

    @requires_pv
    def get_coil_geometry(
        self,
        pl: Plot3D,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> "pv.MultiBlock":
        opt = self.output_parser.find_optstep(opt_step)
        trans = self.output_parser.find_transstep(opt_step, trans_step)
        if not opt or not opt.coilGeometries3D:
            return pv.MultiBlock()

        combined = self.create_coil_geometries(opt_step)

        for pi in pl.coilPlots:
            if pi.dataType == "scalar":
                if trans and pi.id in trans.coilData3D.columns:
                    for idx in combined.keys():
                        if idx is None:
                            continue
                        if (sg := combined[idx]) is not None:
                            data = trans.coilData3D[
                                trans.coilData3D["conductor"] == int(idx)
                            ][pi.id]
                            sg.cell_data[pi.label] = data.to_numpy()
            elif pi.dataType == "vector":
                pass

        if pl.active is not None:
            combined.set_active_scalars(pl.active.label, allow_missing=True)
        return combined

    @requires_pv
    def get_brick_geometry(
        self,
        pl: Plot3D,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> "pv.MultiBlock":
        opt = self.output_parser.find_optstep(opt_step)
        trans = self.output_parser.find_transstep(opt_step, trans_step)
        if not opt or not opt.brickGeometries3D:
            return pv.MultiBlock()

        combined = self.create_brick_geometries(opt_step)

        for pi in pl.coilPlots:
            if pi.dataType == "scalar":
                if trans and pi.id in trans.brickData3D.columns:
                    for idx in combined.keys():
                        if idx is None:
                            continue
                        if (sg := combined[idx]) is not None:
                            data = trans.brickData3D[
                                trans.coilData3D["conductor"] == int(idx)
                            ][pi.id]
                            sg.cell_data[pi.label] = data.to_numpy()
            elif pi.dataType == "vector":
                pass

        if pl.active is not None:
            combined.set_active_scalars(pl.active.label, allow_missing=True)
        return combined

    @requires_pv
    def create_iron_geometry(self, opt_step: int = 1) -> "pv.MultiBlock":
        opt = self.output_parser.find_optstep(opt_step)
        if opt is None or opt.meshGeometries3D is None:
            return pv.MultiBlock()

        geom_iron = opt.meshGeometries3D
        nodes = geom_iron.nodes * 1000
        face_array = []
        if geom_iron.elements:
            for face in geom_iron.elements:
                face_array.append(face[0])
                face_array.extend(face[1:])
        geom = pv.PolyData(nodes, face_array)  # faces

        return pv.MultiBlock([geom])

    @requires_pv
    def get_iron_geometry(
        self,
        pl: Plot3D,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> "pv.MultiBlock":
        trans = self.output_parser.find_transstep(opt_step, trans_step)
        geoms = self.create_iron_geometry(opt_step)
        if not geoms:
            return geoms

        if trans:
            for geom in geoms:
                if not geom:
                    continue
                for pi in pl.meshPlots:
                    if pi.dataType == "scalar":
                        if pi.id in trans.meshData3D.columns:
                            geom.point_data[pi.label] = trans.meshData3D[
                                pi.id
                            ].to_numpy()
                    elif pi.dataType == "vector":
                        pass  # TODO

        if pl.active is not None:
            geoms.set_active_scalars(pl.active.label)

        return geoms

    @requires_pv
    def plot_3d(
        self,
        pl: Plot3D,
        opt_step: int = 1,
        trans_step: int = 1,
        fig_size=(10, 8),
    ) -> "pv.Plotter":
        plotter = self._create_plot(fig_size)

        if coil_geom := self.get_coil_geometry(pl, opt_step, trans_step):
            plotter.add_mesh(coil_geom, color=None)

        if iron_geom := self.get_iron_geometry(pl, opt_step, trans_step):
            plotter.add_mesh(iron_geom)

        if brick_geom := self.get_brick_geometry(pl, opt_step, trans_step):
            plotter.add_mesh(brick_geom)

        if pl.showSpacers:
            if wedge_geom := self.get_endspacer_geometry(pl, opt_step, trans_step):
                plotter.add_mesh(wedge_geom)

        self._set_perspective(plotter)

        return plotter


class RoxiePrintTables:
    """Roxie table output for tabular data"""

    def __init__(self, ib: RoxieInputBuilder, op: RoxieOutputParser) -> None:
        self.input = ib
        self.output = op

    def get_harmonic_coil(
        self, opt_step, trans_step, coil_nr
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Return the harmonic coil table

        :param opt_step: The Optimization step number
        :param trans_step: The transient step number
        :param coil_nr: Number of the harmonic coil
        :return: A set of 3Pandas dataframes to plot: Coil information, Field information, Multipoles
        """
        if step := self.output.find_transstep(opt_step, trans_step):
            if coil := step.harmonicCoils.get(coil_nr, None):
                return self.print_harmonic_coil(coil)
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    def get_design_variables(self, opt_step) -> pd.DataFrame:
        """Return the design variables for opt step
        :param opt_step: The Optimization step number
        :return A DafaFrame containing design variable name and values
        """
        if step := self.output.find_optstep(opt_step):
            return self.print_design_variables(step.designVariables, self.input.design)

        return pd.DataFrame()

    def get_objective_variables(self, opt_step) -> pd.DataFrame:
        """Return the Objectives variables for opt step
        :param opt_step: The Optimization step number
        :return A DafaFrame containing objective variable name and values
        """
        if step := self.output.find_optstep(opt_step):
            return self.print_objective_results(
                step.objectiveResults, self.input.objective
            )

        return pd.DataFrame()

    def print_harmonic_coil(
        self, coil: HarmonicCoil
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Prints a harmonic coil output as Markdown
        :param coil: The Harmonic coil to print
        :return: A set of 3Pandas dataframes to plot: Coil information, Field information, Multipoles
        """
        return (
            pd.DataFrame.from_dict(coil.get_coil_info(), orient="index").T,
            pd.DataFrame.from_dict(coil.get_field_info(), orient="index").T,
            coil.get_table(),
        )

    def print_design_variables(
        self, designVariables: Dict[int, str], input_design: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        if input_design is not None and not input_design.empty:
            dv = designVariables.keys()
            dv_val = designVariables.values()
            dv_name = input_design["string"]
            dv_act = input_design["act"]
            dv_blocks = input_design["bcs"]
            df = pd.DataFrame(
                {
                    "Nr": dv,
                    "Name": dv_name,
                    "Act on": dv_act,
                    "Blocks": dv_blocks,
                    "Value": dv_val,
                },
            )
        else:
            df = pd.DataFrame(
                designVariables,
                columns=["Variable", "Value"],
            )

        return df

    def print_objective_results(
        self, objectives: Dict[int, str], input_objectives: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        if input_objectives is not None and not input_objectives.empty:
            obj = objectives.keys()
            obj_val = objectives.values()
            obj_name = input_objectives["string"]
            obj_s1 = input_objectives["s1"]
            obj_s2 = input_objectives["s2"]
            df = pd.DataFrame(
                {
                    "Nr": obj,
                    "Name": obj_name,
                    "S1": obj_s1,
                    "S2": obj_s2,
                    "Value": obj_val,
                },
            )
        else:
            df = pd.DataFrame(
                objectives,
                columns=["Variable", "Value"],
            )

        return df


class RoxiePlotOutputs:
    """
    Convenience class for plotting roxie outputs.
    Bundles all Required classes for plotting in one class:

    Example usage:

    ```python
    output_file = "/path/to/roxie/output.xml"
    input_file = "/path/to/roxie/input.xml"

    plot_outputs = RoxiePlotOutputs(output_file, input_file)
    ```

    Access to the individual objects:

    - `plot_outputs.output`: `RoxieOutputParser` object
    - `plot_outputs.input`: `RoxieInputBuilder` object
    - `plot_outputs.graphs`: `RoxieGraphsPlotly` object
    - `plot_outputs.plots2d`: `RoxiePlots2D` object
    - `plot_outputs.plots3d`: `RoxiePlots3D` object
    - `plot_outputs.tables`: `RoxiePrintTables` object

    Content is output using Ipython display functions,
    including Headers, plots and tables.
    """

    def __init__(self, output_file: str, input_file: Optional[str]) -> None:
        """Create a new RoxiePlotOutputs object based on the roxie xml output and data file.
        Content is output using Ipython display functions,
        including Headers, plots and tables
        :param output_file: The roxie xml output
        :param input_file: The roxie data file (optional)
        """
        self.output = RoxieOutputParser(xml_file=output_file)
        if input_file:
            self.input = RoxieInputBuilder.from_datafile(input_file)
        else:
            self.input = RoxieInputBuilder()

        self.graphs = RoxieGraphsPlotly(self.output)
        self.plots2d = RoxiePlots2D(self.output)
        self.plots3d = RoxiePlots3D(self.output)
        self.tables = RoxiePrintTables(self.input, self.output)

        self._setup_plots()

    def _setup_plots(self) -> None:
        """Setup plot settings based on input and output files"""
        self.plots2d.mirrorX = self.input.flags["LIMAGX"]
        self.plots2d.mirrorY = self.input.flags["LIMAGY"]

    @staticmethod
    def _print_header(level: int, txt: str) -> None:
        """Print a heading at level
        :param level: The heading level
        :param txt: The heading text
        """
        display(Markdown("#" * level + " " + txt))

    def output_run_summary(self) -> None:
        """Generate a summary of the run"""
        txt = f"""- Run date: {self.output.run_date}
- Roxie version: {self.output.roxie_version} ({self.output.roxie_githash})
- Comment: {self.output.comment}
- {len(self.output.opt)} optimization step(s) with {len(self.output.opt[1].step)} transient step(s)
"""
        display(Markdown(txt))

    def output_design_variables(self, opt_step: int = 1) -> None:
        """Print design variables
        :param opt_step: The Optimization step number
        """
        df = self.tables.get_design_variables(opt_step)
        if not df.empty:
            display(df)

    def output_objective_results(self, opt_step: int = 1) -> None:
        """Print objective results
        :param opt_step: The Optimization step number
        """
        df = self.tables.get_objective_variables(opt_step)
        if not df.empty:
            display(df)

    def output_harmonic_coils(
        self, opt_step: int = 1, trans_step: int = 1, header_level: int = 1
    ) -> None:
        """Print Harmonic coil results
        :param opt_step: The Optimization step number
        :param trans_step: The transient step number
        :param header_level: Header level for each harmonic coil
        """
        trans = self.output.find_transstep(opt_step, trans_step)
        if trans is None:
            return

        for hc, coil in trans.harmonicCoils.items():
            self._print_header(header_level, f"Harmonic coil {hc}")
            dfs = self.tables.print_harmonic_coil(coil)
            for df in dfs:
                display(df.style.hide())
            fig = self.graphs.plot_harmonics(coil, fig_size=(8, 5))
            fig.show()

    def output_conductor_forces(
        self, opt_step: int = 1, trans_step: int = 1, fig_size=(12, 8)
    ) -> None:
        """Print conductor forces for Time step
        :param opt_step: The Optimization step number
        :param trans_step: The transient step number
        :param fig_size: Size of the output figures in inches
        """

        trans = self.output.find_transstep(opt_step, trans_step)
        if trans is None:
            return

        cond_df = trans.conductorForces
        if cond_df is not None:
            p = self.graphs.plot_forces(cond_df, fig_size)
            p.show()
            fig = self.plots2d.plot_conductor_forces(opt_step, trans_step, fig_size)
            if fig:
                plt.show()

    def output_optimization_graphs(
        self, fig_size=(12, 8), plots: Optional[List[int]] = None
    ) -> None:
        """Print all optimization graphs
        :param fig_size: Figure size in inches, defaults to (12,8)
        :param plots: List of plots to print, or None for all
        """
        for plot in self.output.graphs_optimization:
            if plots is None or plot.id in plots:
                p = self.graphs.plot_optimization_graph(plot, fig_size)
                if p:
                    p.show()

    def output_transient_graphs(
        self, opt_step: int = 1, fig_size=(12, 8), plots: Optional[List[int]] = None
    ) -> None:
        """Print all transient graphs
        :param opt_step: Optimization step number, defaults to 1
        :param fig_size: Figure size in inches, defaults to (12,8)
        :param plots: List of plots to print, or None for all
        """
        for plot in self.output.graphs_transient:
            if plots is None or plot.id in plots:
                p = self.graphs.plot_transient_graph(plot, opt_step, fig_size)
                if p:
                    p.show()

    def output_device_graphs(
        self,
        opt_step: int = 1,
        trans_step: int = 1,
        fig_size=(12, 8),
        plots: Optional[List[int]] = None,
    ) -> None:
        """Print all device graphs
        :param opt_step: Optimization step number, defaults to 1
        :param trans_step: Transient step number, defaults to 1
        :param fig_size: Figure size in inches, defaults to (12,8)
        :param plots: List of plots to print, or None for all
        """
        for plot in self.output.graphs_device:
            if isinstance(plot, GraphPlot):
                if plots is None or plot.id in plots:
                    p = self.graphs.plot_device_graph(
                        plot, opt_step, trans_step, fig_size
                    )
                    if p:
                        p.show()

    def output_2dplots(
        self,
        opt_step: int = 1,
        trans_step: int = 1,
        fig_size=(8, 8),
        plots: Optional[List[int]] = None,
    ) -> None:
        """Print all 2d plots
        :param opt_step: Optimization step number, defaults to 1
        :param trans_step: Transient step number, defaults to 1
        :param fig_size: Figure size in inches, defaults to (12,8)
        :param plots: List of plots to print, or None for all
        """
        for plot in self.output.plots2D:
            if plots is None or plot.id in plots:
                _ = self.plots2d.plot_xs(plot, opt_step, trans_step, fig_size)
                plt.show()

    def output_3dplots(
        self,
        opt_step: int = 1,
        trans_step: int = 1,
        fig_size=(10, 8),
        plots: Optional[List[int]] = None,
    ) -> None:
        """Print all 3d plots
        :param opt_step: Optimization step number, defaults to 1
        :param trans_step: Transient step number, defaults to 1
        :param fig_size: Figure size in inches, defaults to (12,8)
        :param plots: List of plots to print, or None for all
        """
        for plot in self.output.plots3D:
            if plots is None or plot.id in plots:
                pl = self.plots3d.plot_3d(plot, opt_step, trans_step, fig_size)
                if pl:
                    pl.show()

    def output_report(self, header_level: int = 1) -> None:
        """Output a full run report
        :param header_level: The level of header to start with (default: 1)
        """

        self._print_header(header_level, "Roxie results")
        self.output_run_summary()

        for os, opt in self.output.opt.items():
            if len(self.output.opt) > 1:
                header_level = header_level + 1
                self._print_header(header_level, f"Optimization step {os}: {opt.name}")

            self.output_design_variables(os)

            self.output_objective_results(os)

            for ts, trans in opt.step.items():
                if len(opt.step) > 1:
                    header_level = header_level + 1
                    self._print_header(
                        header_level, f"Transient step {ts}: {trans.name}"
                    )

                self.output_harmonic_coils(os, ts, header_level + 1)

                self._print_header(header_level + 1, "Plots")

                self.output_conductor_forces(os, ts)
                self.output_device_graphs(os, ts)
                self.output_2dplots(os, ts)
                self.output_3dplots(os, ts)

                if len(opt.step) > 1:
                    header_level = header_level - 1

            if len(opt.transientGraphs) > 0:
                self._print_header(header_level + 1, "Transient graphs")

                self.output_transient_graphs(os)

            if len(self.output.opt) > 1:
                header_level = header_level - 1

        if len(self.output.optimizationGraphs) > 0:
            self._print_header(header_level + 1, "Optimization graphs")
            self.output_optimization_graphs()
