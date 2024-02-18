from dataclasses import dataclass

from _qwak_proto.qwak.feature_store.features.feature_set_pb2 import (
    FeatureSetUserMetadata as ProtoMetadata,
)

_METADATA_ATTRIBUTE = "_qwak_metadata"


def set_metadata_on_function(
    function, owner: str = "", description: str = "", display_name: str = ""
):
    setattr(
        function,
        _METADATA_ATTRIBUTE,
        Metadata(owner=owner, description=description, display_name=display_name),
    )


def get_metadata_from_function(
    function, owner: str = "", description: str = "", display_name: str = ""
):
    return getattr(
        function,
        _METADATA_ATTRIBUTE,
        Metadata(owner=owner, description=description, display_name=display_name),
    )


@dataclass
class Metadata:
    owner: str = ""
    description: str = ""
    display_name: str = ""

    @staticmethod
    def from_proto(metadata: ProtoMetadata):
        return Metadata(metadata.owner, metadata.description, metadata.display_name)

    def to_proto(self):
        return ProtoMetadata(
            owner=self.owner,
            description=self.description,
            display_name=self.display_name,
        )
