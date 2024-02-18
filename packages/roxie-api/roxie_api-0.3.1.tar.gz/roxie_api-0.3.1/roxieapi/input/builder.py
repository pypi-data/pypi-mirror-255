import copy
import logging
import os
from pathlib import Path
from typing import List

import jinja2
import pandas as pd

from roxieapi.commons.types import BrickData
from roxieapi.input.parser import (
    RoxieInputParser,
    convert_bottom_header_table_to_str,
    convert_list_to_str,
    convert_table_to_str,
)


class RoxieInputBuilder:
    """Class RoxieInputBuilder builds a ROXIE input"""

    DEFAULT_VERSION = "23.9.0"
    DEFAULT_FLAGS = {
        "LEND": False,
        "LWEDG": False,
        "LPERS": False,
        "LQUENCH": False,
        "LALGO": False,
        "LQUENCH0D": False,
        "LMIRIRON": False,
        "LBEMFEM": False,
        "LPSI": False,
        "LSOLV": False,
        "LIRON": False,
        "LMORPH": False,
        "LHMO": False,
        "LHARD": False,
        "LPOSTP": False,
        "LPEAK": False,
        "LINMARG": False,
        "LMARG": False,
        "LSELF": False,
        "LMQE": False,
        "LINDU": False,
        "LEDDY": False,
        "LSOLE": False,
        "LFLUX": False,
        "LFIELD3": False,
        "LSELF3": False,
        "LBRICK": False,
        "LLEAD": False,
        "LVRML": False,
        "LOPERA": False,
        "LOPER20": False,
        "LANSYS": False,
        "LRX2ANS": False,
        "LANS2RX": False,
        "LDXF": False,
        "LMAP2D": False,
        "LMAP3D": False,
        "LEXPR": False,
        "LFIL3D": False,
        "LFIL2D": False,
        "LCNC": False,
        "LANSYSCN": False,
        "LWEIRON": False,
        "LCATIA": False,
        "LEXEL": False,
        "LQVOLT": False,
        "LFORCE2D": False,
        "LQUNPLOT": False,
        "LGRAPHCSV": False,
        "LAXIS": False,
        "LIMAGX": False,
        "LIMAGY": False,
        "LRAEND": False,
        "LMARKER": False,
        "LROLER2": False,
        "LROLERP": False,
        "LIMAGZZ": False,
        "LSUPP": False,
        "LSTEP": False,
        "LSKIPDPL": False,
        "LIFF": False,
        "LICCA": False,
        "LICC": False,
        "LICCIND": False,
        "LITERNL": False,
        "LTOPO": False,
        "LQUEN3": False,
        "LAYER": False,
        "LEULER": False,
        "LHEAD": False,
        "LPLOT": False,
        "LVERS52": False,
        "LHARM": False,
        "LMATRF": False,
        "LF3LIN": False,
        "LKVAL": False,
        "LSKIPTPL": False,
    }

    def __init__(self) -> None:
        self.version = RoxieInputBuilder.DEFAULT_VERSION
        self.comment = ""
        self.bhdata_path = ""
        self.cadata_path = ""
        self.iron_path = ""
        self.flags = copy.copy(RoxieInputBuilder.DEFAULT_FLAGS)
        self.global2doption = pd.DataFrame()
        self.global3d = pd.DataFrame()
        self.block = pd.DataFrame()
        self.blockoption = pd.DataFrame()
        self.block3d = pd.DataFrame()
        self.blockoption3d = pd.DataFrame()
        self.lead = pd.DataFrame()
        self.brick: List[BrickData] = []
        self.ironyokeoptions = pd.DataFrame()
        self.ironyoke = pd.DataFrame()
        self.extrusion = pd.DataFrame()
        self.permanentmag2 = pd.DataFrame()
        self.permanentmag1 = pd.DataFrame()
        self.layer = pd.DataFrame()
        self.algo = pd.DataFrame()
        self.design = pd.DataFrame()
        self.euler = pd.DataFrame()
        self.peak: List[int] = []
        self.timetable2 = pd.DataFrame()
        self.timetable1 = pd.DataFrame()
        self.eddy = pd.DataFrame()
        self.eddyoptions = pd.DataFrame()
        self.quenchg = pd.DataFrame()
        self.quenchen = pd.DataFrame()
        self.quenchtm = pd.DataFrame()
        self.quenchp = pd.DataFrame()
        self.quenchs = pd.DataFrame()
        self.harmonictable = pd.DataFrame()
        self.matrf = pd.DataFrame()
        self.matrf_coordsystem = 1  # 1 for cartesian, 2 for polar
        self.linefield = pd.DataFrame()
        self.kvalues = pd.DataFrame()
        self.harmonicoption = pd.DataFrame()
        self.graph = pd.DataFrame()
        self.graphoption = pd.DataFrame()
        self.plot2d = pd.DataFrame()
        self.plot2doption = pd.DataFrame()
        self.plot3d = pd.DataFrame()
        self.plot3doption = pd.DataFrame()
        self.ansysoptions = pd.DataFrame()
        self.objective = pd.DataFrame()
        self.quench0d = pd.DataFrame()

        self.logger = logging.getLogger("RoxieInputBuilder")

    def set_flag(self, flag_name: str, flag_value: bool) -> "RoxieInputBuilder":
        """Method setting a flag in a ROXIE input file. An error is thrown if a flag does not exist
        :param flag_name: name of a flag
        :param flag_value: value of a flag
        :return: an updated RoxieInputBuilder instance
        """
        if flag_name in self.flags.keys():
            self.flags[flag_name] = flag_value
        else:
            raise KeyError("Key")
        return self

    def update_version(self):
        if self.version < "10.1":
            # Harmonic Table
            if not self.harmonictable.empty:
                self.harmonictable.insert(loc=1, column="type", value=1)
                self.harmonictable.insert(loc=4, column="s1", value=0)
                self.harmonictable.insert(loc=5, column="s2", value=0)
        if self.version < "10.1.2":
            # Ironyokeoptions handled in parser
            # Matrf handled in parser
            pass
        if self.version < "10.1.3":
            if self.flags["LSTEP"]:
                self.timetable1.insert(loc=8, column="nsteps", value=0)
        if self.version < "22.0":
            # Block
            if self.flags["LEND"]:
                self.block.insert(loc=12, column="disc", value=21)
            # Block/Block3D helix
            if "4" in self.block["type"]:
                self.logger.warning(
                    "Helix definition in block data from a Datafile < 22.0 found. "
                    + "The definition of Helices changed. Please check your block data"
                )

            # Quench0D
            if not self.quench0d.empty:
                self.quench0d.insert(loc=1, column="tempq", value=0.0)
                self.quench0d.drop("indu", axis=1, inplace=True)
                self.quench0d.insert(loc=4, column="dtdt", value=0.0)
                self.quench0d.insert(loc=5, column="deltm", value=0.0)
                self.quench0d.insert(loc=6, column="currqm", value=0.0)

        # update flags
        old_flags = self.flags.keys() - self.DEFAULT_FLAGS.keys()
        for old_flag in old_flags:
            del self.flags[old_flag]
        new_flags = self.DEFAULT_FLAGS.keys() - self.flags.keys()
        for new_flag in new_flags:
            self.flags[new_flag] = self.DEFAULT_FLAGS[new_flag]

        # Set the new version of the datafile
        self.version = self.DEFAULT_VERSION

    def build(self, output_path: Path) -> None:
        """Method building a ROXIE input based on a template file
        :param output_path: an output path for the input .data file
        """
        output_str = self.prepare_data_file_str_from_template()

        with open(output_path, "wb") as input_file:
            input_file.write(bytes(output_str, "utf-8").replace(b"\r\n", b"\n"))

    def prepare_data_file_str_from_template(self) -> str:
        path = Path(os.path.dirname(__file__))
        template_loader = jinja2.FileSystemLoader(searchpath=path)
        template_env = jinja2.Environment(loader=template_loader)
        template_env.globals[
            "convert_bottom_header_table_to_str"
        ] = convert_bottom_header_table_to_str
        template_env.globals["convert_table_to_str"] = convert_table_to_str
        template_env.globals[
            "convert_flag_dct_to_str"
        ] = RoxieInputBuilder.convert_flag_dct_to_str
        template_env.globals["convert_list_to_str"] = convert_list_to_str
        template_env.globals["str"] = str
        template_env.globals["len"] = len

        TEMPLATE_FILE = "roxie_template.data.j2"
        template = template_env.get_template(TEMPLATE_FILE)
        return template.render(input=self)

    @staticmethod
    def convert_flag_dct_to_str(flags: dict) -> str:
        """Static method converting a dictionary with flags into a formatted string
        :param flags: a dictionary with flags
        :return: a formatted string representation of the dictionary with flags
        """
        COLUMN_WIDTH = 15
        flag_per_line_count = 1
        flag_str = "  "
        for key, value in flags.items():
            temp = "%s=%s" % (key, "T" if value else "F")
            temp += (COLUMN_WIDTH - len(temp)) * " "
            if flag_per_line_count < 6:
                flag_str += temp
                flag_per_line_count += 1
            else:
                flag_str += temp + "\n  "
                flag_per_line_count = 1

        flag_str += "\n  /"
        return flag_str

    @staticmethod
    def from_datafile(filename):
        """Constructs a RoxieInputBuilder, initializing its values from a .data file
        :param filename: The .data file
        :return a constructed RoxieInputBuilder object
        """

        rip = RoxieInputParser.from_datafile(filename)
        b = RoxieInputBuilder()
        b.version = rip.version
        b.comment = rip.comment
        b.cadata_path = rip.cadata_path
        b.bhdata_path = rip.bhdata_path
        b.iron_path = rip.iron_path
        b.flags = rip.options

        b.global2doption = rip.get_block("GLOBAL2DOPTION")
        b.global3d = rip.get_block("GLOBAL3D")
        b.block = rip.get_block("BLOCK")
        b.blockoption = rip.get_block("BLOCKOPTION")
        b.block3d = rip.get_block("BLOCK3D")
        b.blockoption3d = rip.get_block("BLOCKOPTION3D")
        b.lead = rip.get_block("LEAD")
        b.brick = rip.get_bricks()
        b.ironyokeoptions = rip.get_block("IRONYOKEOPTIONS")
        b.ironyoke = rip.get_block("IRONYOKE")
        b.extrusion = rip.get_block("EXTRUSION")
        b.permanentmag2 = rip.get_block("PERMANENTMAG2")
        b.permanentmag1 = rip.get_block("PERMANENTMAG1")
        b.layer = rip.get_block("LAYER")
        b.algo = rip.get_block("ALGO")
        b.design = rip.get_block("DESIGN")
        b.euler = rip.get_block("EULER")
        b.peak = rip.get_peak()
        b.timetable2 = rip.get_block("TIMETABLE2")
        b.timetable1 = rip.get_block("TIMETABLE1")
        b.eddy = rip.get_block("EDDY")
        b.eddyoptions = rip.get_block("EDDYOPTONS")
        b.quenchg = rip.get_block("QUENCHG")
        b.quenchen = rip.get_block("QUENCHEN")
        b.quenchtm = rip.get_block("QUENCHTM")
        b.quenchp = rip.get_block("QUENCHP")
        b.quenchs = rip.get_block("QUENCHS")
        b.harmonictable = rip.get_block("HARMONICTABLE")
        b.matrf_coordsystem = rip.matrf_coordsystem
        b.matrf = rip.get_block("MATRF")
        b.linefield = rip.get_block("LINEFIELD")
        b.kvalues = rip.get_block("KVALUES")
        b.harmonicoption = rip.get_block("HARMONICOPTION")
        b.graph = rip.get_block("GRAPH")
        b.graphoption = rip.get_block("GRAPHOPTION")
        b.plot2d = rip.get_block("PLOT2D")
        b.plot2doption = rip.get_block("PLOT2DOPTION")
        b.plot3d = rip.get_block("PLOT3D")
        b.plot3doption = rip.get_block("PLOT3DOPTION")
        b.objective = rip.get_block("OBJECTIVE")
        b.ansysoptions = rip.get_block("ANSYSOPTIONS")
        b.quench0d = rip.get_block("QUENCH0D")

        return b
