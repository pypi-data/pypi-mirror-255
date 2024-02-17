from amsdal_data.connections.historical_base import HistoricalConnectionBase as HistoricalConnectionBase
from amsdal_data.manager import AmsdalDataManager as AmsdalDataManager
from amsdal_utils.classes.metadata_manager import MetadataInfoQueryBase
from amsdal_utils.models.data_models.metadata import Metadata as Metadata
from amsdal_utils.models.data_models.reference import Reference

class MetadataInfoQuery(MetadataInfoQueryBase):
    @classmethod
    def _lakehouse_resource(cls) -> str: ...
    @classmethod
    def _lakehouse_connection(cls) -> HistoricalConnectionBase: ...
    @classmethod
    def get_reference_to(cls, metadata: Metadata) -> list[Reference]: ...
    @classmethod
    def get_referenced_by(cls, metadata: Metadata) -> list[Reference]: ...
