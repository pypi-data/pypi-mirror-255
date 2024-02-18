"""Assonant class to handle writing data from AssonantDataClasses into files."""

import os
from typing import List

from assonant.data_classes import AssonantDataClass

from ._assonant_file_writer_interface import IAssonantFileWriter
from ._file_writer_factory import FileWriterFactory


class AssonantFileWriter(IAssonantFileWriter):
    """Assonant File Writer. Wrapper class to deal with writing data from AssonantDataClass into files.

    Wrapper class that abstracts all process related to creating specific file writers,
    writing data on files following the requirements of the given format.
    """

    _factory = FileWriterFactory()

    def __init__(self, file_format: str):
        # Persist file format
        self.file_format = file_format

        # Create specific file writer based on chosen file format
        self.file_writer = self._factory.create_file_writer(file_format)

    def write_data(self, filepath: str, filename: str, data: AssonantDataClass):
        """Method for writing data using the specific FileWriter respective to define file format.

        If fail to save on target filepath, in order to avoid losing acquired data, it will try
        to save locally in current working directory.

        Args:
            filepath (str): Path where file will be saved.
            filename (str): Name that will be given to file.
            data (AssonantDataClass): AssonantDataClass that contains data to be saved in file.
        """
        try:
            self.file_writer.write_data(filepath, filename, data)
        except Exception as e:
            workdir_filepath = os.path.join(os.getcwd())
            print(
                f"Failed to save data at {filepath} due the following exception: {repr(e)}. Trying to save file locally in current work directory..."
            )
            try:
                self.file_writer.write_data(workdir_filepath, filename, data)
                print(f"File saved at current work directory (path: {workdir_filepath})")
            except Exception as e:
                print("Failed to save data locally in current work directory. Data lost.")
                raise e

    def get_supported_file_formats(self) -> List[str]:
        """Getter method for current supported file formats.

        Returns:
            List[str]: List containing curretly supported file formats.
        """
        return self._factory.get_supported_file_formats()
