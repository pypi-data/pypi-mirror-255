from amsdal_utils.classes.metadata_manager import MetadataInfoQueryBase
from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.data_models.metadata import Metadata
from amsdal_utils.models.data_models.reference import Reference
from amsdal_utils.models.enums import Versions
from amsdal_utils.query.utils import Q

from amsdal_data.connections.historical_base import HistoricalConnectionBase
from amsdal_data.manager import AmsdalDataManager


class MetadataInfoQuery(MetadataInfoQueryBase):
    @classmethod
    def _lakehouse_resource(cls) -> str:
        return AmsdalConfigManager().get_config().resources_config.lakehouse

    @classmethod
    def _lakehouse_connection(cls) -> HistoricalConnectionBase:
        return AmsdalDataManager().get_connection_manager().get_connection(cls._lakehouse_resource())  # type: ignore[return-value]

    @classmethod
    def get_reference_to(cls, metadata: Metadata) -> list[Reference]:
        lakehouse_resource = cls._lakehouse_resource()
        lakehouse_connection = cls._lakehouse_connection()
        reference_address = Address.from_string(f'{lakehouse_resource}#Reference::')

        return [
            Reference(**{'ref': result['to_address']})
            for result in lakehouse_connection.query(
                reference_address,
                conditions=(
                    Q(from_address__class_name=metadata.address.class_name)
                    & Q(from_address__object_id=metadata.address.object_id)
                    & Q(from_address__object_version=metadata.address.object_version)
                ),
            )
        ]

    @classmethod
    def get_referenced_by(cls, metadata: Metadata) -> list[Reference]:
        lakehouse_resource = cls._lakehouse_resource()
        lakehouse_connection = cls._lakehouse_connection()
        reference_address = Address.from_string(f'{lakehouse_resource}#Reference::')
        version_q = Q(to_address__object_version=metadata.address.object_version)

        if metadata.is_latest:
            version_q |= Q(to_address__object_version='') | Q(to_address__object_version=Versions.LATEST)

        return [
            Reference(**{'ref': result['from_address']})
            for result in lakehouse_connection.query(
                reference_address,
                conditions=(
                    Q(to_address__class_name=metadata.address.class_name)
                    & Q(to_address__object_id=metadata.address.object_id)
                    & version_q
                ),
            )
        ]
