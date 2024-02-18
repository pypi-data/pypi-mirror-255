import logging
import string
import xml.etree.ElementTree as et
from io import StringIO
from typing import Dict, List, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd

from roxieapi.commons.types import (
    Brick3DGeometry,
    Coil3DGeometry,
    CoilGeometry,
    Geometry,
    GraphInfo,
    GraphPlot,
    HarmonicCoil,
    Plot2D,
    Plot3D,
    PlotAxis,
    PlotInfo,
    PlotLegend,
    WedgeGeometry,
    WedgeSurface,
)


class TransStepData:
    """Data of a transient step"""

    def __init__(self, id: int, name: str) -> None:
        self.id: int = id
        self.name: str = name
        self.coilData = pd.DataFrame()
        self.meshData = pd.DataFrame()
        self.matrixData = pd.DataFrame()
        # self.irisData = pd.DataFrame()
        self.coilData3D = pd.DataFrame()
        self.brickData3D = pd.DataFrame()
        self.meshData3D = pd.DataFrame()
        self.deviceGraphs: Dict[int, pd.DataFrame] = {}
        self.harmonicCoils: Dict[int, HarmonicCoil] = {}
        self.conductorForces: Optional[pd.DataFrame] = None


class OptData:
    """Data Of an optimization Step"""

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name: str = name
        self.coilGeometries: Dict[int, CoilGeometry] = {}
        self.coilGeometries3D: Dict[int, Coil3DGeometry] = {}
        self.brickGeometries3D: Dict[int, Brick3DGeometry] = {}
        self.wedgeGeometries3D: Dict[int, WedgeGeometry] = {}
        self.meshGeometries: Optional[Geometry] = None
        self.meshGeometries3D: Optional[Geometry] = None
        self.transientGraphs: Dict[int, pd.DataFrame] = {}
        self.step: Dict[int, TransStepData] = {}
        self.designVariables: Dict[int, str] = {}
        self.objectiveResults: Dict[int, str] = {}


class RoxieOutputParser:
    """Roxie output parser class.

    Takes all different Roxie outputs, parses them, and provides a structured output of the results.
    """

    _PLOTINFOS = {
        "coilPlotInfo": "coilPlot",
        "meshPlotInfo": "meshPlot",
        "coilPlot3DInfo": "coilPlot3D",
        "meshPlot3DInfo": "meshPlot3D",
        "matrixPlotInfo": "matrixPlot",
        "irisPlotInfo": "irisPlot",
        "pointPlotInfo": "pointPlot",
    }

    def __init__(self, xml_file: str) -> None:
        self.logger = logging.getLogger("RoxieOutputParser")

        self.optimizationGraphs: Dict[
            int, pd.DataFrame
        ] = {}  # Result values on optimization graphs, (id)
        self.opt: Dict[int, OptData] = {}

        self.plots2D: List[Plot2D] = []  # 2D Plots information for device
        self.plots3D: List[Plot3D] = []  # 3D Plots information for device
        self.graphs_device: List[GraphPlot] = []  # Graph information for device
        self.graphs_transient: List[
            GraphPlot
        ] = []  # Plot information for transient plots
        self.graphs_optimization: List[
            GraphPlot
        ] = []  # Plot information for optimization plots

        xtree = et.parse(xml_file)
        self.xroot = xtree.getroot()

        self._fill_sim_info()
        self._fill_plot_info()
        self._fill_runs()

    def _fill_sim_info(self) -> None:
        """Fill the basic information from a simulation"""
        self.roxie_version = self.xroot.attrib["version"]
        self.roxie_githash = self.xroot.attrib["git_hash"]
        self.run_date = self.xroot.attrib["runDate"]
        self.comment = self.xroot.attrib["comment"]

    def _fill_plot_info(self) -> None:
        piTag = self.xroot.find("plottingInfos")
        if not piTag:
            return

        # Extract plotInfo objects first:
        plotInfos: List[PlotInfo] = []
        for pi in piTag:
            if pi.tag in self._PLOTINFOS.keys():
                plotInfos.append(self._extract_plotinfo(pi))

        for pi in piTag:
            if pi.tag == "graphPage":
                self._extract_graph_info(pi)
            elif pi.tag == "pageXsec":
                self._extract_plot2d_info(pi, plotInfos)
            elif pi.tag == "page3D":
                self._extract_plot3d_info(pi, plotInfos)

    def _fill_runs(self) -> None:
        for run in self.xroot.findall("loop/step"):
            runId = int(run.attrib["id"])
            runname = run.attrib["label"]
            opt = OptData(runId, runname)
            self.opt[runId] = opt

            loop = run.find("loop")
            if loop:
                if trans_graphs := loop.find("graphData"):
                    opt.transientGraphs = self._extract_graph_data(
                        trans_graphs, "graph"
                    )
                for st in loop.findall("step"):
                    stepId = int(st.attrib["id"])
                    step = TransStepData(stepId, st.attrib["label"])
                    opt.step[stepId] = step
                    self._extract_device_plots(step, st)

            self._fill_geometries(run, opt)
        self._fill_dv_objectives()
        if opt_graph := self.xroot.find("loop/graphData"):
            self.optimizationGraphs = self._extract_graph_data(opt_graph, "graph")

    def _extract_plotinfo(self, elem: et.Element) -> PlotInfo:
        id = elem.attrib["id"]
        leg = elem.find("legend")
        plotLegend = None
        if leg is not None:
            attr = leg.attrib
            plotLegend = PlotLegend(
                attr.get("pos", "w"),
                attr.get("greyScale") == "true",
                float(attr["min"]) if attr.get("min") else None,
                float(attr["max"]) if attr.get("max") else None,
            )
        dataType = elem.attrib["dataType"]
        lbl = elem.attrib["label"]
        harmCoil = None
        if (hc := elem.attrib.get("harm_coil", "0")) != "0":
            harmCoil = int(hc)

        vector_mappings = {}
        if dataType == "vector":
            if id_x := elem.attrib.get("data_x", None):
                vector_mappings["x"] = int(id_x)
            if id_y := elem.attrib.get("data_y", None):
                vector_mappings["y"] = int(id_y)
            if id_z := elem.attrib.get("data_z", None):
                vector_mappings["z"] = int(id_z)

        return PlotInfo(
            id,
            self._PLOTINFOS[elem.tag],
            dataType,
            lbl,
            plotLegend,
            harmCoil,
            vector_mappings,
        )

    def _extract_plot2d_info(
        self, elem: et.Element, plotInfosAll: List[PlotInfo]
    ) -> None:
        t = elem.find("title")
        id = int(elem.attrib["id"])
        if t:
            title = t.attrib["label"]
        else:
            title = "Plot2D {0}".format(id)
        axes = self._extract_axes_info(elem)

        plotInfos: List[PlotInfo] = []
        for pi in self._PLOTINFOS.values():
            pps = [pp.attrib["id"] for pp in elem.findall(pi)]
            plotInfos.extend(
                filter(lambda x: x.type == pi and x.id in pps, plotInfosAll)
            )
        p2d = Plot2D(title, id, axes, plotInfos.copy())

        self.plots2D.append(p2d)

    def _extract_plot3d_info(
        self, elem: et.Element, plotInfosAll: List[PlotInfo]
    ) -> None:
        id = int(elem.attrib["id"])
        if t := elem.find("title"):
            title = t.attrib["label"]
        else:
            title = "Plot3D {0}".format(id)
        axes = self._extract_axes_info(elem)

        plotInfos: List[PlotInfo] = []
        for pi in self._PLOTINFOS.values():
            pps = [pp.attrib["data_id"] for pp in elem.findall(pi)]
            plotInfos.extend(
                filter(lambda x: x.type == pi and x.id in pps, plotInfosAll)
            )
        p3d = Plot3D(title, id, axes, plotInfos.copy())

        self.plots3D.append(p3d)

    def _extract_graph_info(self, elem: et.Element) -> None:
        id = int(elem.attrib["id"])
        graphTypes = []
        graphList: List[GraphInfo] = []
        for plot in elem.findall("graphPlot"):
            graphTypes.append(int(plot.attrib["graphType"]))

            graphList.append(
                GraphInfo(
                    int(plot.attrib["id"]),
                    int(plot.attrib["graphType"]),
                    plot.attrib["xval"],
                    plot.attrib["yval"],
                    bool(plot.attrib["logX"]),
                    bool(plot.attrib["logY"]),
                    float(plot.attrib["weight"]),
                    plot.attrib.get("label", None),
                )
            )

        title = elem.attrib.get("title", f"Graph {id}")
        axes = self._extract_axes_info(elem)

        gp = GraphPlot(title, id, axes, graphList.copy())
        if 1 in graphTypes:
            self.graphs_device.append(gp)
        if 2 in graphTypes:
            self.graphs_transient.append(gp)
        if 3 in graphTypes:
            self.graphs_optimization.append(gp)

    def _extract_axes_info(self, elem: et.Element) -> Dict[str, PlotAxis]:
        axes: Dict[str, PlotAxis] = {}
        for axis in elem:
            if not axis.tag.startswith("axis"):
                continue
            ax = axis.tag[-1]
            lbl = axis.attrib.get("label", "")
            log = axis.attrib.get("log", "false").lower() == "true"
            min = axis.attrib.get("min", None)
            max = axis.attrib.get("max", None)
            bounds = (float(min), float(max)) if min and max else None
            axes[ax] = PlotAxis(lbl, bounds, log)
        return axes

    def _fill_dv_objectives(self) -> None:
        for it in self.xroot.findall("loop/optimizationResults/iteration"):
            itId = int(it.attrib["nr"])
            if itId not in self.opt:
                raise Exception(
                    f"Error in XML file: Iteration {itId} is not in optimization steps"
                )
            for obj in it.findall("objectives/objective"):
                objId = int(obj.attrib["nr"])
                self.opt[itId].objectiveResults[objId] = obj.attrib["value"]
            for dv in it.findall("designVariables/variable"):
                dvId = int(dv.attrib["nr"])
                self.opt[itId].designVariables[dvId] = dv.attrib["value"]

    def _extract_device_plots(self, step: TransStepData, stepRoot: et.Element) -> None:
        step.harmonicCoils = self._extract_harmonic_coils(stepRoot)
        for child in stepRoot:
            if child.tag == "conductorForces":
                step.conductorForces = self._extract_csv_table(child)
            elif child.tag == "coilData":
                step.coilData = self._extract_csv_table(child)
            elif child.tag == "coilData3D":
                step.coilData3D = self._extract_csv_table(child)
            elif child.tag == "brickData3D":
                step.brickData3D = self._extract_csv_table(child)
            elif child.tag == "meshData":
                step.meshData = self._extract_csv_table(child)
            elif child.tag == "meshData3D":
                step.meshData3D = self._extract_csv_table(child)
            elif child.tag == "matrixData":
                step.matrixData = self._extract_csv_table(child)
            elif child.tag == "graphData":
                step.deviceGraphs = self._extract_graph_data(child, "graph")
            elif child.tag == "harmonicCoil":
                pass
            else:
                self.logger.error(f"Data object not implemented: {child.tag}")

    def _extract_coilgeom3d_data(
        self, root: et.Element
    ) -> dict[int, Dict[int, pd.DataFrame]]:
        target: Dict[int, Dict[int, pd.DataFrame]] = {}
        for cableData in root.findall("coilData3D"):
            id_coil = int(cableData.attrib["data_id"])
            id_name = "id"
            target[id_coil] = self._extract_geom_data(
                cableData, "cableData", id_name=id_name
            )
        return target

    def _extract_matrix_data(self, root: et.Element) -> Optional[pd.DataFrame]:
        d = root.find("matrixData")
        if d is None:
            return None
        return self._xml_to_df(d, nodenames="d")

    def _extract_geom_data(
        self, root: et.Element, name: str, id_name: str = "id"
    ) -> Dict[int, pd.DataFrame]:
        target: Dict[int, pd.DataFrame] = {}
        for d in root.findall(name):
            id = int(d.attrib[id_name])
            df = self._xml_to_df(d, nodenames="d")
            if df is not None:
                target[id] = df
        return target

    def _extract_csv_table(self, root: et.Element) -> pd.DataFrame:
        df = pd.read_csv(StringIO(root.text), header=0)
        df.rename(columns=lambda x: x.strip(), inplace=True)
        return df

    def _extract_graph_data(
        self, root: et.Element, name: str
    ) -> Dict[int, pd.DataFrame]:
        target: Dict[int, pd.DataFrame] = {}
        for d in root.findall(name):
            id = int(d.attrib["id"])
            target[id] = self._extract_csv_table(d)
        return target

    def _extract_harmonic_coils(self, step: et.Element) -> "Dict[int, HarmonicCoil]":
        coils = {}
        for elem in step.findall("harmonicCoil"):
            hc = self._create_harmonic_coil(elem)
            coils[hc.id] = hc

        return coils

    def _create_harmonic_coil(self, elem: et.Element) -> HarmonicCoil:
        bn = {}
        an = {}
        params = {}
        id = None
        measurement_type = None
        main_harmonic = None
        coil_type = None
        for k, v in elem.attrib.items():
            if k == "id":
                id = int(v)
            elif k == "meas_type":
                measurement_type = int(v)
            elif k == "main_harmonic":
                main_harmonic = int(v)
            elif k == "coil_type":
                coil_type = int(v)
            else:
                params[k] = float(v)
        harms = elem.find("harmonics")
        if harms:
            for harm in harms.findall("harmonic"):
                order = int(harm.attrib["order"])
                bn[order] = float(harm.attrib["b"])
                an[order] = float(harm.attrib["a"])

        if (sc := elem.find("strandContributions")) is not None:
            strandData = self._extract_csv_table(sc)
        else:
            strandData = pd.DataFrame()

        assert id is not None
        assert measurement_type is not None
        assert main_harmonic is not None
        assert coil_type is not None
        return HarmonicCoil(
            id, coil_type, measurement_type, main_harmonic, params, bn, an, strandData
        )

    def _fill_geometries(self, run: et.Element, opt: OptData) -> None:
        for geom in run:
            if geom.tag == "coilGeom":
                opt.coilGeometries = self._extract_coils_2D(geom)
            elif geom.tag == "coilGeom3D":
                opt.coilGeometries3D = self._extract_coils_3D(geom)
            elif geom.tag == "meshGeom":
                opt.meshGeometries = self._extract_mesh(geom)
            elif geom.tag == "meshGeom3D":
                opt.meshGeometries3D = self._extract_mesh(geom)
            elif geom.tag == "brickGeom3D":
                opt.brickGeometries3D = self._extract_bricks_3d(geom)
            elif geom.tag == "wedgeGeom3D":
                opt.wedgeGeometries3D = self._extract_wedges_3D(geom)

    def _extract_mesh(self, root: et.Element) -> Optional[Geometry]:
        nData = root.find("nodes")
        if nData is None:
            raise Exception("Error in meshGeometry: Nodes missing")
        df = self._xml_to_df(nData, "p")
        nodes = df.to_numpy()
        elements = None
        if eData := root.find("elements"):
            elements = self._extract_mesh_elements(eData)
        boundaries = None
        if bData := root.find("boundaries"):
            boundaries = self._extract_mesh_boundaries(bData)

        return Geometry(nodes, elements, boundaries)

    def _extract_coils_2D(self, root: et.Element) -> Dict[int, CoilGeometry]:
        cables = {}
        for cable in root.findall("cable"):
            cable_nr = int(cable.attrib.get("nr", 0))
            block_nr = int(cable.attrib.get("block_nr", 0))
            layer_nr = int(cable.attrib.get("layer_nr", 0))
            df = self._xml_to_df(cable)
            cable_points = df[["x", "y"]].to_numpy(dtype=np.float64)
            strands = {}
            for strand in cable.findall("strands/strand"):
                strand_nr = int(strand.attrib["nr"])
                df = self._xml_to_df(strand)
                strands[strand_nr] = df[["x", "y"]].to_numpy(dtype=np.float64)
            cables[cable_nr] = CoilGeometry(
                cable_nr, block_nr, layer_nr, cable_points, strands
            )

        return cables

    def _extract_bricks_3d(self, root: et.Element) -> Dict[int, Brick3DGeometry]:
        geoms = {}
        for brick in root.findall("brick"):
            df = self._xml_to_df(brick)
            id = int(brick.get("nr", 0))
            nodes = df[["x", "y", "z"]].to_numpy(dtype=np.float64)
            elements = self._generate_coil_cells(nodes)
            geoms[id] = Brick3DGeometry(id, Geometry(nodes, elements, None))
        return geoms

    def _extract_coils_3D(self, root: et.Element) -> Dict[int, Coil3DGeometry]:
        geoms = {}
        for cable in root.findall("cable"):
            cableId = int(cable.attrib.get("nr", 0))
            df = self._xml_to_df(cable)
            nodes = df[["x", "y", "z"]].to_numpy(dtype=np.float64)
            elements = self._generate_coil_cells(nodes)
            geoms[cableId] = Coil3DGeometry(
                nr=cableId,
                block_id=int(cable.attrib.get("block_nr", 0)),
                layer_id=int(cable.attrib.get("layer_nr", 0)),
                geometry=Geometry(
                    nodes,
                    elements,
                    None,
                ),
            )
        return geoms

    def _extract_wedges_3D(self, root: et.Element) -> Dict[int, WedgeGeometry]:
        wedges: Dict[int, WedgeGeometry] = {}
        for spacer in root.findall("spacer"):
            spacer_id = int(spacer.attrib["nr"])
            layer_id = int(spacer.attrib["layer_nr"])
            block_inner = int(spacer.attrib.get("block_outer", "-1"))
            block_outer = int(spacer.attrib.get("block_inner", "-1"))

            surfaces: Dict[str, Optional[WedgeSurface]] = {}
            place = ["inner", "outer"]
            pos = ["lower", "upper"]
            for p in place:
                edges: Dict[str, npt.NDArray[np.float64]] = {}
                for pp in pos:
                    spacer_el = spacer.find(f"{p}/{pp}")
                    if spacer_el:
                        df = self._xml_to_df(spacer_el)
                        edges[pp] = df[["x", "y", "z"]].to_numpy(dtype=np.float64)
                if all(pp in edges for pp in pos):
                    surfaces[p] = WedgeSurface(edges["lower"], edges["upper"])
                else:
                    surfaces[p] = None

            wedges[spacer_id] = WedgeGeometry(
                layer_id,
                spacer_id,
                surfaces["inner"],
                surfaces["outer"],
                block_inner,
                block_outer,
            )

        return wedges

    def _generate_coil_cells(self, nodes: npt.NDArray[np.float64]) -> List[List[int]]:
        """Generate cells from points.
           points are ordered in z direction, 4 points define one face.
           Once cell is between two sets of 4 points

          7+----+6
          /|   /|
        3+----+2|
         |4+--|-+5
         |/   |/
        0+----+1
        """
        elements = [[8] + list(range(i - 4, i + 4)) for i in range(4, len(nodes), 4)]
        return elements

    def _generate_coil_faces(self, nodes: npt.NDArray[np.float64]) -> List[List[int]]:
        p_per_elem = 4
        elements = [[p_per_elem] + list(range(p_per_elem))]
        L: int = len(nodes)
        for i in range(0, L, p_per_elem):
            for j in range(p_per_elem):
                elements.append(
                    [
                        p_per_elem,
                        i + j,
                        i + (j + 1) % p_per_elem,
                        i + j + p_per_elem,
                        i + (j + 1) % p_per_elem + p_per_elem,
                    ]
                )
        elements.append([p_per_elem] + list(range(L - 4, L)))
        return elements

    def _extract_mesh_elements(self, root: et.Element) -> Optional[List[List[int]]]:
        results = []
        for elem in root.findall("fe"):
            cnt = int(elem.attrib["cnt"])
            entry = [cnt]
            for x in string.ascii_lowercase[0:cnt]:
                entry.append(int(elem.attrib[x]) - 1)
            results.append(entry)
        return results

    def _extract_mesh_boundaries(
        self, root: et.Element, elements: List[str] = ["x", "y"]
    ) -> Dict[int, npt.NDArray[np.float64]]:
        df: Optional[pd.DataFrame] = self._xml_to_df(root)
        boundaries: Dict[int, npt.NDArray[np.float64]] = {}
        if df is not None:
            for f, vals in df.groupby("f"):
                boundaries[f] = vals[elements].to_numpy(dtype=np.float64)  # type: ignore
        return boundaries

    def _xml_to_df(self, root: et.Element, nodenames: str = "p") -> pd.DataFrame:
        dicts = [x.attrib for x in root.findall(nodenames)]
        df = pd.DataFrame(dicts)
        c: str
        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="ignore")
        return df

    def find_transstep(self, opt_step: int, trans_step: int) -> Optional[TransStepData]:
        if opt_step in self.opt and trans_step in self.opt[opt_step].step:
            return self.opt[opt_step].step[trans_step]
        return None

    def find_optstep(self, opt_step) -> Optional[OptData]:
        return self.opt.get(opt_step, None)

    def get_harmonic_coil(
        self,
        coil_nr: int = 1,
        opt_step: int = 1,
        trans_step: int = 1,
    ) -> Optional[HarmonicCoil]:
        """Return the harmonic coil for given step and coil id, or None if not present

        :param coil_nr: Harmonic Coil Nr, defaults to 1
        :param opt_step: The Optimization Step Nr, defaults to 1
        :param trans_step: The Transient Step Nr, defaults to 1
        :return: The Harmonic coil, or None
        """
        if trans := self.find_transstep(opt_step, trans_step):
            return trans.harmonicCoils.get(coil_nr, None)
        return None

    def get_conductor_forces(
        self, opt_step: int = 1, trans_step: int = 1
    ) -> Optional[pd.DataFrame]:
        """Return Conductor forces for given Step, or None if not present

        :param opt_step: The Optimization step, defaults to 1
        :param trans_step: Transient step, defaults to 1
        :return: The Conductor forces as Dataframe
        """
        if trans := self.find_transstep(opt_step, trans_step):
            return trans.conductorForces
        else:
            return None

    def get_crosssection_plot(self, plot_nr: int = 1) -> Optional[Plot2D]:
        """Return the Crossection 2D plot with number i

        :param plot_nr: The plot_number, defaults to 1
        :return: The Plot2D object, or None
        """
        for pl in self.plots2D:
            if isinstance(pl, Plot2D) and pl.id == plot_nr:
                return pl
        return None

    def get_3d_plot(self, plot_nr: int = 1) -> Optional[Plot3D]:
        """Return the 3D plot with number i
        :param plon_nr: The plot number, defaults to 1
        :return: The Plot3D definition, or None
        """
        for pl in self.plots3D:
            if isinstance(pl, Plot3D) and pl.id == plot_nr:
                return pl
        return None
