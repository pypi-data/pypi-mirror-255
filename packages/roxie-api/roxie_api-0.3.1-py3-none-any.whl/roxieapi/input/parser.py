import itertools
import re
from io import StringIO
from typing import Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from roxieapi.commons.types import BrickData


def convert_bottom_header_table_to_str(
    block_df: pd.DataFrame, keyword: str, line_suffix="", header_suffix=""
) -> str:
    """Function converting a dataframe with a keyword and suffix to string. The string is used to create a ROXIE .data
    input file.

    :param block_df: a dataframe with content to be converted into a bottom header table string
    :param keyword: a keyword for the table
    :param line_suffix: a string added at the end of each of line to match the ROXIE formatting
    :return: a string representation of a bottom header table
    """
    if header_suffix:
        keyword_and_length_str = "%s %s" % (keyword, header_suffix)
    else:
        keyword_and_length_str = "%s %d" % (keyword, len(block_df))
    if block_df.empty:
        return keyword_and_length_str
    else:
        if block_df.dtypes.iloc[-1] == object:
            block_df[block_df.columns[-1]] = block_df[block_df.columns[-1]].transform(
                lambda x: " ".join([str(a) for a in x]) if isinstance(x, list) else x
            )
        block_str: str = block_df.to_string(index=False)
        block_str_lines = block_str.split("\n")
        block_str_lines = block_str_lines[1:] + [block_str_lines[0]]
        block_str = (line_suffix + "\n").join(block_str_lines)
        return "%s\n%s" % (keyword_and_length_str, block_str)


def convert_table_to_str(block_df: pd.DataFrame, keyword: str, header_suffix="") -> str:
    """Function converting a dataframe with a keyword and suffix to string without bottom header columns.
    The string is used to create a ROXIE .datainput file.

    :param block_df: a dataframe with content to be converted into a bottom header table string
    :param keyword: a keyword for the table
    :param line_suffix: a string added at the end of each of line to match the ROXIE formatting
    :return: a string representation of a bottom header table
    """
    if header_suffix:
        keyword_and_length_str = "%s %s" % (keyword, header_suffix)
    else:
        keyword_and_length_str = "%s %d" % (keyword, len(block_df))

    block_str: str = block_df.to_string(index=False)
    block_str_lines = block_str.split("\n")
    # header at the first index is skipped
    block_str = "\n".join(block_str_lines[1:])
    return "%s\n%s" % (keyword_and_length_str, block_str)


def convert_list_to_str(input: List[int]) -> str:
    return "  " + "".join(["{0:4d}".format(v) for v in input])


def read_bottom_header_table(roxie_file_path: str, keyword="CABLE") -> pd.DataFrame:
    """Function reading a bottom header table from ROXIE .data, .cadata, .output files

    :param roxie_file_path: a path to a roxie file
    :param keyword: a table keyword
    :return: a dataframe with content of a table given by a keyword
    """
    with open(roxie_file_path, "r") as text_file:
        text_file_lines = text_file.read().split("\n")

    index_start, n_lines = find_index_start_and_length_bottom_header_table(
        text_file_lines, keyword
    )
    return extract_bottom_header_table(text_file_lines, index_start, n_lines)


def find_index_start_and_length_bottom_header_table(
    output_lines: List[str], table_keyword: str
) -> Tuple[int, int]:
    """Function finding the start and length of a table in ROXIE .output or .cadata or .data file.
    If a table keyword can't be found, the an IndexError is thrown.

    :param output_lines: a list of lines read from a ROXIE file
    :param table_keyword: a keyword for the objective table
    :return: a tuple with an index of the start of bottom header table and its length
    """
    len_keyword = len(table_keyword)
    for index_line, output_line in enumerate(output_lines):
        if (len(output_line) >= len_keyword) and (
            output_line[0:len_keyword] == table_keyword
        ):
            index_table_start = index_line
            matches = re.findall(r"\d+", output_line)
            if matches:
                n_lines_table = int(matches[0])
                return index_table_start, n_lines_table

    raise IndexError("Not found start index and length for keyword %s" % table_keyword)


def extract_bottom_header_table(
    text_file_lines: List[str], index_start: int, n_lines: int
) -> pd.DataFrame:
    """Function extracting a bottom header template from ROXIE .data and .cadata files.
    The method requires a start index
    in the table as well as the number of lines the table occupies.

    :param text_file_lines: an input list of lines from a ROXIE .data or .cadata file
    :param index_start: an index where the table starts
    :param n_lines: the number of lines occupied by the table
    :return: a dataframe with the table
    """
    value_rows = text_file_lines[index_start + 1 : index_start + n_lines + 1]
    header = text_file_lines[index_start + n_lines + 1]
    if "Comment" in header:
        columns = ",".join(header.split()[:-1])
    else:
        columns = ",".join(header.split())

    # Replace comment
    values_comma_separated = []
    comments = []
    for value_row in value_rows:
        if "'" in value_row:
            quotation_split = value_row.split("'")
            values_without_comment = ",".join(quotation_split[0].split())
            values_comma_separated.append(values_without_comment)
            comments.append(quotation_split[1])
        else:
            values_comma_separated.append(",".join(value_row.split()))

    TESTDATA = StringIO("\n".join([columns] + values_comma_separated))
    objective_table_df = pd.read_csv(TESTDATA, sep=",")
    if comments:
        objective_table_df["Comment"] = comments
    return objective_table_df


def read_nested_bottom_header_table(
    roxie_file_path: str, keyword="LAYER"
) -> pd.DataFrame:
    """Function reading a bottom header table from ROXIE .data, .cadata, .output files

    :param roxie_file_path: a path to a roxie file
    :param keyword: a table keyword
    :return: a nested dataframe with content of a table given by a keyword
    """
    with open(roxie_file_path, "r") as text_file:
        text_file_lines = text_file.read().split("\n")

    index_start, n_lines = find_index_start_and_length_bottom_header_table(
        text_file_lines, keyword
    )

    return extract_nested_bottom_header_table(text_file_lines, index_start, n_lines)


def extract_nested_bottom_header_table(
    text_file_lines: List[str], index_start: int, n_lines: int
):
    """Function extracting a bottom header template from ROXIE .data and .cadata files.
    The method requires a start index
    in the table as well as the number of lines the table occupies.

    :param text_file_lines: an input list of lines from a ROXIE .data or .cadata file
    :param index_start: an index where the table starts
    :param n_lines: the number of lines occupied by the table
    :return: a dataframe with the table
    """
    value_rows = text_file_lines[index_start + 1 : index_start + n_lines + 1]
    headers = text_file_lines[index_start + n_lines + 1].split()

    header_values = []
    for value_row in value_rows:
        header_value: Dict[str, Union[int, float, str, List[Union[int, str]]]] = {}
        values = value_row.split()
        for index, header in enumerate(headers[:-1]):
            try:
                header_value[header] = int(values[index])
                continue
            except ValueError:
                pass
            try:
                header_value[header] = float(values[index])
                continue
            except ValueError:
                pass
            header_value[header] = values[index]

        # It is assumed that the remaining values for a list assigned to the last column
        # Thus it starts from len(headers) - 1 until the last but one element (the last one is \ character)
        remaining_values = values[len(headers) - 1 : -1]

        header_value[headers[-1]] = [
            int(value) if value.isdigit() else value for value in remaining_values
        ]
        header_values.append(header_value)

    return pd.DataFrame(header_values)


def peek(it):
    first = next(it)
    return first, itertools.chain([first], it)


class RoxieInputParser:
    """Class RoxieInputParser parses a roxie file"""

    def __init__(self, inputlines: Iterable[str]):
        """Constructor. Creates a new input parser from list of lines
        :param inputlines: list of lines within datafile
        """
        self.lines = itertools.filterfalse(lambda x: x == "" or x.isspace(), inputlines)
        self.execdict = {
            "IRONYOKEOPTIONS": lambda x, y: self._parse_ironyokeoptions(),
            "ALGO": lambda x, y: self._parse_table(1, "ALGO"),
            "EDDY": lambda x, y: self._parse_table(1, "EDDY"),
            "BRICK": lambda x, y: self._parse_bricks(int(y)),
            "ANSYSOPTIONS": lambda x, y: self._parse_ansysoptions(),
            "QUENCH0D": lambda x, y: self._parse_table(1, "QUENCH0D"),
            "PEAK": lambda x, y: self._parse_peaks(int(y)),
            "MATRF": lambda x, y: self._parse_matrf(int(y)),
        }
        # fields
        self.version: Optional[str] = None
        self.comment = None
        self.bhdata_path = None
        self.cadata_path = None
        self.iron_path = None
        self.options: Dict[str, str] = {}
        self.blocks: Dict[str, pd.DataFrame] = {}
        self.bricks: List[BrickData] = []
        self.peaks: List[int] = []
        self.matrf_coordsystem = 0

    def _parse_matrf(self, coord_type: int):
        """Parse MATRF block of roxie .data file
        :param coord_type: The Coordinate system of Field vector matrix
                           (1-> Cartesian, 2->Polar)
        """
        self.matrf_coordsystem = coord_type
        df = self._parse_table(3, "MATRF")
        if "field" in df:
            field_val = int(df.iloc[-1, -1])  # type:ignore
            df = df.astype({"field": str})
        else:
            field_val = 0
        df["field"] = ""
        df.iloc[-1, -1] = str(field_val)
        return df

    def get_block(self, blockname):
        """Return the data of a block
        :param blockname: The name of the block
        :return A filled Dataframe for regular blocks, a list of Daraframes for "special" blocks,
                or an empty Dataframe of no block was initialized
        """

        if blockname in self.blocks:
            return self.blocks[blockname]
        else:
            return pd.DataFrame()

    @staticmethod
    def from_datafile(inputfile):
        """Construct a new RoxieInputParser from Roxie .data file
        :param inputfile: Roxie .data file
        :return: A RoxieInputParser object with parsed content
        """
        with open(inputfile, "r") as f:
            input_lines = [x.strip() for x in f.readlines()]
        rip = RoxieInputParser(input_lines)
        rip._parse_datafile()
        return rip

    def _parse_datafile(self):
        """Method to parse the contents of a .data file"""
        self._parse_headers()
        self._parse_blocks()

    def _parse_headers(self) -> None:
        line = next(self.lines)
        if line.strip().startswith("VERSION"):
            self.version = self._parse_version(line)
            line = next(self.lines)
        else:
            self.version = "09"
        self.comment = self._parse_quoted(line)
        self.bhdata_path = self._parse_quoted(next(self.lines))
        self.cadata_path = self._parse_quoted(next(self.lines))
        line = next(self.lines)
        if not line.strip().startswith("&OPTION"):
            self.iron_path = self._parse_quoted(line)
            next(self.lines)
        self._parse_options()

    def _parse_quoted(self, line):
        """Method to parse a quoted string (e.g comment, bhdata,cadata,iron paths)"""
        m = re.match(r"'([^']*)'", line)
        if m:
            return m[1]
        else:
            return line

    def _parse_version(self, line):
        """Method to parse the Version of a roxie file"""
        m = re.match(r"VERSION ([^$]+)", line)
        if m:
            return m[1]
        else:
            raise Exception("Cannot parse version string")

    def _parse_blocks(self):
        """Method to parse all remaining blocks of the input"""
        while True:
            try:
                line = next(self.lines)
                if not line or line.isspace():
                    # Skip whitespace
                    pass
                else:
                    m = re.match(r"(&?[\w]+)\W?([\d/]+){0,1}", line)
                    if m:
                        val = self.execdict.get(
                            m[1], lambda x, y: self._parse_table(int(y), x)
                        )(m[1], m[2])
                        if val is not None:
                            self.blocks[m[1]] = val
            except StopIteration:
                # End of loading. Break out of the while loop
                break

    def _parse_options(self):
        """Method to parse the &Options section of a .data file"""
        while True:
            opline = next(self.lines)
            matches = re.findall(r"([\w]+)=(T|F)", opline)
            for m, t in matches:
                self.options[m] = t == "T"
            if "/" in opline:
                break
        return None

    def _parse_table(self, nrLines, option=""):
        """Method to parse a table with n lines.
        :param nrLines: Number of lines to parse (excluding header)
        :param option: The name of the table (optional, unused for now)
        :return A Dataframe with the parsed table content
        """
        if nrLines == 0:
            return pd.DataFrame()
        else:
            tbl_lines = [next(self.lines) for i in range(nrLines + 1)]
            if tbl_lines[0].strip()[-1] == "/":
                return extract_nested_bottom_header_table(tbl_lines, -1, nrLines)
            else:
                return extract_bottom_header_table(tbl_lines, -1, nrLines)

    def _parse_peaks(self, nrElems) -> None:
        """Method to parse a list with n elements (e.g PEAK in .data file)
        :param nrElems: Number of elements of list
        """
        if nrElems > 0:
            entries = next(self.lines).split()
            self.peaks = [int(entry) for entry in entries]
        else:
            self.peaks = []

    def _parse_ironyokeoptions(self):
        """Method to parse the IRONYOKEOPTIONS section of a .data file
        :return a list of dataframes: [scale, radmu,symtype,symcond,symmode]
        """

        # For roxie versions < 10.1.1, only symcond exists
        if self.version and self.version < "10.1.2":
            df_scale = pd.DataFrame([[1]], columns=["scale"])
            df_rad_mu = pd.DataFrame([[0, 0]], columns=["inrad", "reperm"])
            df_symcond = self._parse_table(1, "IRONYOKEOPTIONS_SYMCOND")
            df_symtype = pd.DataFrame([[0]], columns=["symtype"])
            df_symmode = pd.DataFrame([[1, 0, 0]], columns=["mode", "div", "sym"])
        else:
            df_scale = self._parse_table(1, "IRONYOKEOPTIONS_SCALE")
            df_rad_mu = self._parse_table(1, "IRONYOKEOPTIONS_RIRPERM")
            df_symtype = self._parse_table(1, "IRONYOKEOPTIONS_SYMTYPE")
            df_symcond = self._parse_table(1, "IRONYOKEOPTIONS_SYMCOND")
            df_symmode = self._parse_table(1, "IRONYOKEOPTIONS_SYMMODE")
        return pd.concat(
            [df_scale, df_rad_mu, df_symtype, df_symcond, df_symmode], axis=1
        )

    def _parse_ansysoptions(self):
        """Method to parse the ANSYSOPTIONS section of a .data file
        :return a list of dataframes: [ansysscale,rx2ansyscs,ansysoptions_offsets]
        """
        df_ansysscale = self._parse_table(1, "ANSYSOPTIONS_SCALE").rename(
            columns={"scale": "scale1"}
        )
        df_rx2ansys_cs = self._parse_table(1, "ANSYSOPTIONS_RX2ANSYSCS").rename(
            columns={"scale": "scale2"}
        )
        df_offsets = self._parse_table(1, "ANSYSOPTIONS_OFFSETS")
        return pd.concat([df_ansysscale, df_rx2ansys_cs, df_offsets], axis=1)

    def _parse_bricks(self, nrLines: int) -> None:
        """Parse Roxie Additional brick input
        Args:
            nrLines (int): Number of Brick definitions
        Returns:
            List[BrickData]: A list of Brick elements
        """
        bricks = []
        for i in range(nrLines):
            brick_data = next(self.lines).split()
            nr_nodes = int(brick_data[3])
            nodes = np.genfromtxt(self.lines, max_rows=nr_nodes * 4)

            brick = BrickData(
                float(brick_data[0]),
                int(brick_data[1]),
                int(brick_data[2]),
                int(brick_data[4]),
                nodes,
            )
            bricks.append(brick)
        self.bricks = bricks
        return None

    def get_bricks(self) -> List[BrickData]:
        """Returns the list of all bricks .
        Returns:
            List[BrickData]: the Bricks as BrickData list
        """
        return self.bricks

    def get_peak(self) -> List[int]:
        """Return list of peak field enabled blocks"""
        return self.peaks
