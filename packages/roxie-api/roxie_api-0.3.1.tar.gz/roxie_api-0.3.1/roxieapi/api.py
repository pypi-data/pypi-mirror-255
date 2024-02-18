import importlib.resources as pkg_resources

import papermill as pm

from roxieapi import notebooks
from roxieapi.output.forces import (  # noqa: F401
    convert_roxie_force_file_to_ansys as convert_roxie_force_file_to_ansys,
)
from roxieapi.output.forces import (  # noqa: F401
    update_force2d_with_field_scaling as update_force2d_with_field_scaling,
)
from roxieapi.output.plots import RoxiePlotOutputs as RoxiePlotOutputs


def plot_roxie_report(datafile_path: str, xml_path: str) -> None:
    """From a generated xml output and a roxie data file, print a report style output to
    the current jupyter notebook (markdown + plots), including all plots, graphs and tables

    :param datafile_path: Path to the datafile
    :param xml_path: Path to the generated xml
    """
    rpo = RoxiePlotOutputs(xml_path, datafile_path)
    rpo.output_report()


def generate_roxie_report(
    datafile_path: str, xml_path: str, notebook_output_path: str
) -> None:
    """Generate a ipynb notebook report for a given datafile and output

    :param datafile_path: Input datafile
    :param xml_path: Input generated xml file (from roxie run)
    :param notebook_output_path: The generated report
    """
    notebook_template = pkg_resources.files(notebooks) / "roxie_report_template.ipynb"
    pm.execute_notebook(
        notebook_template,
        notebook_output_path,
        parameters=dict(file_data=datafile_path, file_xml=xml_path),
    )
