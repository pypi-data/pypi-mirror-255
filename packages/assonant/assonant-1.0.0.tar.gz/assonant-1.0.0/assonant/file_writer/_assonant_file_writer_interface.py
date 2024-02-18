from abc import ABC, abstractmethod

from assonant.data_classes import AssonantDataClass


class IAssonantFileWriter(ABC):
    """Assonant File Writer Interface.

    This interface defines what must be implemented by a class to be a File Writer
    in Assonant environment
    """

    @abstractmethod
    def write_data(self, filepath: str, filename: str, data: AssonantDataClass):
        """Method resposible for writing data from AssonantDataClasses into a specific file format.

        Args:
            filepath (str): Path where file will be saved.
            filename (str): Name that will be given to file.
            data (AssonantDataClass): AssonantDataClass that contains data to be saved in file.
        """
