import datetime
import fnmatch
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import requests

from roxieapi.input.builder import RoxieInputBuilder


class RoxieToolAdapter(ABC):
    """A RoxieToolAdapter class with methods to execute a ROXIE model from
    command line, read figures of merit table and prepare a Lorentz force
    file."""

    def __init__(
        self,
        input_files: List[Path],
    ) -> None:
        """A constructor of a RoxieToolAdapter instance.

        :param input_files: A list of input files for the execution
            (data file, iron file, cadata file, bhdata file)
        :param output_file_path: a name of an output file, .output
        :param xml_output_file_path: a name of an xml output file with
            plots, .xml
        """
        self.input_files: Dict[str, Path] = {}
        self.needs_datafile_update = False
        self._collect_input_files(input_files)
        self._check_file_deps()
        self.input_builder = self._sync_file_deps()

        self.output: str = ""
        self.errors: str = ""

    def _collect_input_files(self, input_files: List[Path]) -> None:
        for file in input_files:
            ending = file.suffix
            if ending == ".hmo":
                ending = ".iron"
            if ending in self.input_files:
                raise ValueError(
                    f"File {file} would replace existing file: {self.input_files[ending]}"
                )
            self.input_files[ending] = file.absolute()
        if ".data" not in self.input_files:
            raise ValueError("Datafile is missing in input files")

    def _sync_file_deps(self) -> RoxieInputBuilder:
        """Synchronize file paths between input files and datafile inputs.

        Iterates through input files and datafile inputs and
        synchronizes both. Input files in the constructor have priority
        over files mentioned in the datafile.
        """
        needs_change = False
        rib = RoxieInputBuilder.from_datafile(self.input_files[".data"])

        for file_type, file_path in [
            (".cadata", "cadata_path"),
            (".bhdata", "bhdata_path"),
            (".iron", "iron_path"),
        ]:
            if file_type in self.input_files:
                setattr(rib, file_path, str(self.input_files[file_type]))
                needs_change = True
            elif fp := getattr(rib, file_path).strip():
                if fp == "none":
                    continue
                path = Path(fp)
                if path.is_absolute():
                    self.input_files[file_type] = path
                else:
                    self.input_files[file_type] = (
                        self.input_files[".data"].parent / path
                    )

        self.needs_datafile_update = needs_change
        self._check_file_deps()

        return rib

    def _check_file_deps(self) -> None:
        """Check if all files are accessible and can be used.

        :raises ValueError: In case one file cannot be accessed
        """
        for ft, file in self.input_files.items():
            if not file.is_file():
                raise ValueError(f"Cannot read {ft} file: {file}")

    def download_artefacts(self, output_directory: Path, *patterns) -> None:
        """Downloads artefacts based on the given patterns to the specified
        output directory.

        Args:
            output_directory (Path): The directory where the artefacts will be downloaded.
            *patterns: Variable length argument list of patterns to filter artefacts.

        Returns:
            None
        """
        artefacts = self.get_artefact_list()
        artefacts_filtered: Set[str] = set()
        if not patterns:
            artefacts_filtered.update(artefacts)
        else:
            for pat in patterns:
                matching = fnmatch.filter(artefacts, pat)
                artefacts_filtered.update(matching)

        for artefact in artefacts_filtered:
            self.download_artefact(output_directory, artefact)

    @abstractmethod
    def get_artefact_list(self) -> list[str]:
        raise NotImplementedError("This method is not implemented for this class")

    @abstractmethod
    def run(self) -> int:
        """Execute a ROXIE simulation."""
        raise NotImplementedError("This method is not implemented for this class")

    @abstractmethod
    def download_artefact(self, output_directory: Path, artefact: str) -> None:
        """A method to download an artefact to the specified output directory.

        Args:
            output_directory (Path): The directory where the artefact will be downloaded.
            artefact (str): The name of the artefact to be downloaded.

        Returns:
            None
        """
        raise NotImplementedError("This method is not implemented for this class")


class RestRoxieToolAdapter(RoxieToolAdapter):
    def __init__(
        self,
        service_url: str,
        input_files: List[Path],
        session: Optional[requests.Session] = None,
    ) -> None:
        """Initializes the object with the provided service URL and input
        files.

        :param service_url: The URL of the service to connect to. (str)
        :param input_files: The input files to use. (List[Path])
        :param session: An optional existing session to use
        """
        super().__init__(input_files=input_files)

        self.base_url = service_url
        self.model_name: Optional[str] = None
        self.timestamp: Optional[str] = None
        if session:
            self.session = session
        else:
            self.session = requests.Session()

    def _update_datafile(self):
        """Update datafile to define all paths relative."""
        if cadata := self.input_files.get("cadata"):
            self.input_builder.cadata_path = cadata.name
        if bhdata := self.input_files.get("bhdata"):
            self.input_builder.bhdata_path = bhdata.name
        if iron := self.input_files.get("iron"):
            self.input_builder.iron_path = iron.name

        # Create temporary file
        tmp_data_filename = Path(tempfile.gettempdir()) / self.input_files[".data"].name
        self.input_builder.build(tmp_data_filename)
        self.input_files[".data"] = tmp_data_filename

    def run(self) -> int:

        self._update_datafile()

        self.model_name = self.input_files[".data"].stem

        # get timestamp
        response = self.session.post(
            urljoin(self.base_url, f"/model/{self.model_name}")
        )
        response.raise_for_status()

        self.timestamp = response.json()["timestamp"]

        # upload input files
        data = {"model_name": self.model_name, "timestamp": self.timestamp}
        response = self.session.post(
            urljoin(self.base_url, "/model"),
            data=data,
            files=[("files", open(fp, "rb")) for _, fp in self.input_files.items()],
        )
        response.raise_for_status()

        # Run
        response = self.session.post(
            urljoin(self.base_url, f"/model/{self.model_name}/{self.timestamp}/run")
        )
        response.raise_for_status()

        response_json = response.json()

        self.output = response_json["output"]
        self.errors = response_json.get("errors", "")
        self.model_name = response_json["model_name"]
        self.timestamp = response_json["timestamp"]
        status = response_json["status"]

        return 0 if status else 1

    def get_artefact_list(self) -> List[str]:
        """Return a list of artefacts available to download.

        :return: The list of artefacts
        """
        if self.model_name is None or self.timestamp is None:
            raise RuntimeError(
                "No execution results avaible, Model needs to run sucessfully first"
            )
        artefactlist_url = urljoin(
            self.base_url, f"/artefacts/{self.model_name}/{self.timestamp}"
        )
        response = self.session.get(artefactlist_url)
        response.raise_for_status()
        return response.json()["artefacts"]

    def download_artefact(self, output_directory: Path, artefact: str) -> None:
        if self.model_name is None or self.timestamp is None:
            raise RuntimeError(
                "No execution results avaible, Model needs to run sucessfully first"
            )
        if not output_directory.is_dir():
            raise RuntimeError(f"Output path {output_directory} is not a directory")
        artefact_url = urljoin(
            self.base_url, f"artefact/{self.model_name}/{self.timestamp}/{artefact}"
        )
        response_artefact = self.session.get(artefact_url)
        response_artefact.raise_for_status()
        with open(Path(output_directory) / artefact, "wb") as file:
            file.write(response_artefact.content)


class TerminalRoxieToolAdapter(RoxieToolAdapter):
    def __init__(
        self,
        input_files: List[Path],
        run_in_tmp_folder: bool = True,
        tmp_path_parent: Optional[str] = None,
        executable_name: str = "runroxie",
        overwrite_arguments: Optional[List[str]] = None,
    ):
        """Initialize the RoxieTooladapter with the given input files and
        configuration options.

        :param input_files: List of input files for the
            RoxieTooladapter. (List[Path])
        :param run_in_tmp_folder: Flag to run the RoxieTooladapter in a
            temporary folder. Defaults to True. (bool)
        :param tmp_path: Parent Path to the temporary folder. Temporary
            folder will be created here Defaults to None.
            (Optional[str])
        :param executable_name: Name of the executable. Defaults to
            "runroxie". (str)
        :param overwrite_arguments: List of arguments to overwrite.
            Defaults to None. (Optional[List[str]])
        :raises RuntimeError: If run_in_tmp_folder is False and datafile
            needs to be updated.
        :return: None
        :rtype: None
        """
        super().__init__(input_files)
        self.executable_name = executable_name
        self.artefact_list: Set[Path] = set()
        self.tmp_folder: Optional[TemporaryDirectory]
        if run_in_tmp_folder:
            self.tmp_folder = TemporaryDirectory(dir=tmp_path_parent)
            self.exec_folder = Path(self.tmp_folder.name)
            for p in [
                self.input_builder.cadata_path,
                self.input_builder.bhdata_path,
                self.input_builder.iron_path,
            ]:
                if not Path(p.strip()).is_absolute():
                    self.needs_datafile_update = True
                    self.input_builder.cadata_path = (
                        str(self.input_files[".cadata"])
                        if ".cadata" in self.input_files
                        else ""
                    )
                    self.input_builder.bhdata_path = (
                        str(self.input_files[".bhdata"])
                        if ".bhdata" in self.input_files
                        else ""
                    )
                    self.input_builder.iron_path = (
                        str(self.input_files[".iron"])
                        if ".iron" in self.input_files
                        else ""
                    )
        else:
            self.tmp_folder = None
            self.exec_folder = self.input_files[".data"].parent

        self.overwrite_arguments = overwrite_arguments
        if not run_in_tmp_folder and self.needs_datafile_update:
            raise RuntimeError(
                "Datafile needs to be rewritten but run in tmp folder is deactivated. "
                "RoxieTooladapter does not overwrite existing datafiles. Change execution to run int tmp_folder "
                "or fix paths in data file."
            )

    def _get_process_command(self) -> List[str]:
        if self.overwrite_arguments:
            args = self.overwrite_arguments
        else:
            args = [self.input_files[".data"].name]
        return [self.executable_name, *args]

    def run(self) -> int:
        # Different execution modes depending on the operating system

        if self.needs_datafile_update:
            if not self.tmp_folder:
                raise RuntimeError(
                    "Datafile needs to be rewritten but run in tmp folder is deactivated. "
                    "RoxieTooladapter does not overwrite existing datafiles. Change execution to run int tmp_folder "
                    "or fix paths in data file."
                )
            tmp_data_file = Path(self.tmp_folder.name) / self.input_files[".data"].name
            self.input_builder.build(tmp_data_file)
            self.input_files[".data"] = tmp_data_file

        command = self._get_process_command()
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self.exec_folder)

        exec_timestamp = datetime.datetime.now()

        byte_output, byte_error = p.communicate(
            b"input data that is passed to subprocess' stdin"
        )
        retcode = p.returncode
        byte_output_decode = byte_output.decode()
        byte_error_decode = byte_error.decode()
        self.output = byte_output_decode
        self.errors = byte_error_decode

        modified_files = {
            f
            for f in Path(self.exec_folder).iterdir()
            if datetime.datetime.fromtimestamp(f.stat().st_mtime) > exec_timestamp
        }

        self.artefact_list = modified_files

        return retcode

    def get_artefact_list(self) -> List[str]:
        return [f.name for f in self.artefact_list]

    def download_artefact(self, output_directory: Path, artefact: str) -> None:
        fn = self.exec_folder / artefact
        if not fn.exists():
            raise RuntimeError(f"Artefact {artefact} does not exist in output")
        if not output_directory.is_dir():
            raise RuntimeError(f"Output path {output_directory} is not a directory")

        shutil.copy(fn, output_directory)
