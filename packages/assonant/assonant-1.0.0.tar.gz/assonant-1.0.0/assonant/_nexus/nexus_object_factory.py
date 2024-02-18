"""Factory class to deal with NeXus Object Creation."""


from typing import Dict, List

from nexusformat.nexus import *

from assonant.data_classes import AssonantDataClass
from assonant.data_classes.data_handlers import (
    Axis,
    DataField,
    DataHandler,
    ExternalLink,
    TimeSeries,
)
from assonant.data_classes.instruments import BVS, Detector, Mirror, Monochromator, Slit
from assonant.data_classes.non_instruments import Entry, Sample

from .exceptions import NeXusObjectFactoryError


class NeXusObjectFactory:
    """NeXus Object Factory Class.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating NeXus object out of AssonantDataClass objects.
    """

    def __init__(self):
        self.classes_converted_to_group = [
            Entry,
            Sample,
            Detector,
            Monochromator,
            BVS,
            Mirror,
            Slit,
            TimeSeries,
        ]
        self.classes_converted_to_field = [ExternalLink, DataField, Axis]

    def create_nxobject(self, data_obj: AssonantDataClass, pack_into_nxroot: bool = False) -> NXobject:
        """Creates the respective Nexus object based on the passed AssonantDataClass specific type.

        Args:
            data_obj (AssonantDataClass): Data object which will be used for the
            NeXus object creation
            pack_into_nxroot (bool, optional): If returned object should be or not
            packed inside a NXroot. Defaults to False.

        Raises:
            NeXusObjectFactoryError: The 'obj' argument type does not fit any of the
            supported types

        Returns:
            NXobject: NeXus object respective to the data object passed as the
            data_obj argument
        """
        if isinstance(data_obj, Entry):
            print("Constructor Called: ExperimentEntry")
            nxobject = self._create_entry(data_obj)
        elif isinstance(data_obj, Sample):
            print("Constructor Called: Sample")
            nxobject = self._create_sample(data_obj)
        elif isinstance(data_obj, Detector):
            print("Constructor Called: Detector")
            nxobject = self._create_detector(data_obj)
        elif isinstance(data_obj, Monochromator):
            print("Constructor Called: Monochromator")
            nxobject = self._create_monochromator(data_obj)
        elif isinstance(data_obj, BVS):
            print("Constructor Called: BVS")
            nxobject = self._create_bvs(data_obj)
        elif isinstance(data_obj, Mirror):
            print("Constructor Called: Mirror")
            nxobject = self._create_mirror(data_obj)
        elif isinstance(data_obj, Slit):
            print("Constructor Called: Slit")
            nxobject = self._create_slit(data_obj)
        elif isinstance(data_obj, TimeSeries):
            print("Constructor Called: TimeSeries")
            nxobject = self._create_time_series(data_obj)
        elif isinstance(data_obj, DataField):
            print("Constructor Called: Datafield")
            nxobject = self._create_data_field(data_obj)
        elif isinstance(data_obj, ExternalLink):
            print("Constructor Called: ExternalLink")
            nxobject = self._create_external_link(data_obj)
        else:
            raise NeXusObjectFactoryError(
                f"NeXus object factory doesn't have an constructor method to deal with objects of type: {type(data_obj)}"
            )

        # Check if there are subgroups to be created based on special fields
        if hasattr(data_obj, "fields"):
            print("Constructor Called: 'fields' Dictionary")
            nxobject = self._create_collection_from_dict(nxobject, data_obj.fields)

        if hasattr(data_obj, "positions"):
            print("Constructor Called: Transformations")
            nxobject = self._create_transformations(nxobject, data_obj.positions)

        return NXroot(nxobject) if pack_into_nxroot is True else nxobject

    def _create_entry(self, entry: Entry) -> NXentry:
        """Private method to create the NeXus object respective to any Entry data class.

        Args:
            entry (Entry): Data object containing entry data

        Returns:
            NXentry: NeXus object respective to the Entry data object
        """
        nx_scope_name = "instrument"
        nxobject = NXentry(name=entry.scope_type.value)
        nxobject.insert(NXinstrument(name=nx_scope_name))

        for instrument in entry.instruments:
            nxobject[nx_scope_name].insert(self.create_nxobject(instrument))

        if entry.sample is not None:
            nxobject.insert(self.create_nxobject(entry.sample))

        return nxobject

    def _create_sample(self, sample: Sample) -> NXsample:
        """Private method to create the NeXus object respective to the Sample data class.

        Args:
            sample (Sample): Data object containing sample data

        Returns:
            NXsample: NeXus object respective to the Sample data object
        """
        nx_scope_name = "sample"
        nxobject = NXsample(name=nx_scope_name)
        nxobject["name"] = sample.name

        return nxobject

    def _create_detector(self, detector: Detector) -> NXdetector:
        """Private method to create the NeXus object respective to the Detector data class.

        Args:
            detector (Detector): Data object containing detector data

        Returns:
            NXdetector: NeXus object respective to the Detector data object
        """
        nxobject = NXdetector(name=detector.name)

        return nxobject

    def _create_monochromator(self, monochromator: Monochromator) -> NXmonochromator:
        """Private method to create the NeXus object respective to the Monochromator data class.

        Args:
            monochromator (Monochromator): Data object containing monochromator
            data

        Returns:
            NXmonochromator: NeXus object respective to the Monochromator data
            object
        """
        nxobject = NXmonochromator(name=monochromator.name)

        return nxobject

    def _create_bvs(self, bvs: BVS) -> NXdetector:
        """Private method to create the NeXus object respective to the BVS data class.

        Args:
            bvs (BVS): Data object containing BVS data

        Returns:
            NXdetector: NeXus object respective to the BVS data object
        """
        nxobject = NXdetector(name=bvs.name)

        return nxobject

    def _create_mirror(self, mirror: Mirror) -> NXmirror:
        """Private method to create the NeXus object respective to the Mirror data class.

        Args:
            mirror (Mirror): Data object containing mirror data

        Returns:
            NXmirror: NeXus object respective to the Mirror data object
        """
        nxobject = NXmirror(name=mirror.name)

        return nxobject

    def _create_slit(self, slit: Slit) -> NXslit:
        """Private method to create the NeXus object respective to the Slit data class.

        Args:
            slit (Slit): Data object containing slit data

        Returns:
            NXslit: NeXus object respective to the Slit data object
        """
        nxobject = NXslit(name=slit.name)

        return nxobject

    def _create_external_link(self, external_link: ExternalLink) -> NXlink:
        """Private method to create the NeXus object respective to the ExternalLink data class.

        Args:
            external_link (ExternalLink): Data object containing external link
            data

        Returns:
            NXlink: NeXus object respective to the ExternalLink data object
        """
        nxobject = NXlink(name=external_link.name, target=external_link.target_path, file=external_link.filepath)

        return nxobject

    def _create_time_series(self, time_series: TimeSeries) -> NXlog:
        """Private method to create the NeXus object respective to the TimeSeries data class.

        Args:
            time_series (TimeSeries): Data object containing time_series data

        Returns:
            NXlog: NeXus object respective to the TimeSeries data object
        """
        nxobject = NXlog(
            value=self.create_nxobject(time_series.value),
            time=self.create_nxobject(time_series.timestamps),
        )

        return nxobject

    def _create_data_field(self, data_field: DataField) -> NXfield:
        """Private method to create the NeXus object respective to the Field data class.

        Args:
            data_field (DataField): Data object containing a single field
            data with its respective unit

        Returns:
            NXfield: NeXus object respective to the Field data object
        """
        attrs = data_field.extra_metadata

        if data_field.unit is not None:
            attrs["unit"] = data_field.unit

        nxobject = NXfield(value=data_field.value, attrs=attrs)

        return nxobject

    def _create_transformations(self, nxobject: NXobject, positions: List[Axis]) -> NXobject:
        """Create a NXtransformations group to store positioning data passed as a list of Axis objects.

        Args:
            nxobject (NXobject): NeXus object containing current objects
            positions (List[Axis]): List of Axis objects containing each of them the positioning data related to a
            specific monitored axis.

        Returns:
           NXobject: Respective NXobject with a NXcollection group containing all fields passed.
        """
        if positions != []:
            nxtransformations = NXtransformations(name="transformations")
            for axis in positions:
                nxtransformations[axis.name] = self.create_nxobject(axis.value)
                if isinstance(nxtransformations[axis.name], NXfield):
                    nxtransformations[axis.name].attrs["transformation_type"] = axis.transformation_type.value
                elif isinstance(nxtransformations[axis.name], NXlog):
                    nxtransformations[axis.name]["value"].attrs["transformation_type"] = axis.transformation_type.value
                else:
                    raise NeXusObjectFactoryError(
                        f"Type {nxtransformations[axis.name]} is an invalid conversion type for 'value' field from Axis object"
                    )
            nxobject.insert(nxtransformations)
        return nxobject

    def _create_collection_from_dict(self, nxobject: NXobject, data_dict: Dict[str, DataHandler] = {}) -> NXobject:
        """Create a NXcollection group to store data passed on 'data' dictionary.

        Each key, value tuple from the dictionary will be converted in a field with name equal to the tuple key.

        Args:
            nxobject (NXobject): NeXus object containing current objects
            data_dict (Dict): Dictionary containing data to populate NXcollection group that will be created. Defaults
            to {}.

        Raises:
            NeXusObjectFactoryError: Happens when a not supported AssonantDataClass is used on "data" dict values.

        Returns:
            NXobject: Respective NXobject with a NXcollection group containing all fields passed.
        """
        if data_dict != {}:
            for key in data_dict.keys():
                if isinstance(data_dict[key], DataField):
                    nxobject[key] = self.create_nxobject(data_dict[key])
                elif isinstance(data_dict[key], TimeSeries):
                    nxobject[key] = self.create_nxobject(data_dict[key])
                else:
                    raise NeXusObjectFactoryError(f"Expected 'data_dict[{key}]' to be a DataField or a TimeSeries")
        return nxobject
