import urllib.parse
from typing import Any

from amsdal_models.classes.model import Model
from amsdal_models.classes.utils import get_custom_properties

from amsdal_server.apps.common.serializers.fields_restriction import FieldsRestriction


class ObjectDataMixin:
    @classmethod
    def build_object_data(
        cls,
        item: Model,
        *,
        include_metadata: bool = False,
        fields_restrictions: dict[str, FieldsRestriction] | None = None,
        load_references: bool = False,
    ) -> dict[str, Any]:
        if load_references:
            _item_data = item.model_dump()
        else:
            _item_data = item.model_dump_refs()

        for name in get_custom_properties(item.__class__):
            _item_data[name] = getattr(item, name)

        if include_metadata:
            _metadata = item.get_metadata().model_dump()
            _item_data['_metadata'] = _metadata

            metadata_restrictions = fields_restrictions.get('Metadata', None) if fields_restrictions else None
            if metadata_restrictions and metadata_restrictions.fields:
                new_metadata = {k: v for k, v in _metadata.items() if k in metadata_restrictions.fields}
                # we really want to filter ot fields if thy are valid
                if new_metadata:
                    _item_data['_metadata'] = new_metadata

            _item_data['_metadata']['lakehouse_address'] = urllib.parse.quote(item.get_metadata().address.to_string())
        else:
            _item_data.pop('_metadata', None)

        return _item_data
