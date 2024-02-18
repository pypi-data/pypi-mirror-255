from amsdal.schemas.manager import SchemaManager
from amsdal_models.classes.errors import AmsdalClassError
from amsdal_models.classes.manager import ClassManager
from amsdal_models.classes.model import Model
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS
from amsdal_models.schemas.data_models.schema import ObjectSchema
from amsdal_utils.models.data_models.address import Address
from starlette.authentication import BaseUser

from amsdal_server.apps.classes.errors import ClassNotFoundError
from amsdal_server.apps.classes.mixins.column_info_mixin import ColumnInfoMixin
from amsdal_server.apps.common.mixins.permissions_mixin import PermissionsMixin
from amsdal_server.apps.common.serializers.objects_response import ObjectsResponse
from amsdal_server.apps.objects.mixins.object_data_mixin import ObjectDataMixin
from amsdal_server.apps.objects.utils import apply_version_to_address


class ObjectVersionsApi(PermissionsMixin, ColumnInfoMixin, ObjectDataMixin):
    @classmethod
    def get_object_versions(
        cls,
        user: BaseUser,
        address: str,
        version_id: str = '',
        *,
        all_versions: bool = False,
        include_metadata: bool = True,
    ) -> ObjectsResponse:
        _address = Address.from_string(address)
        schema_manager = SchemaManager()
        schema: ObjectSchema | None = schema_manager.get_schema_by_name(
            _address.class_name,
        )

        try:
            schema_type = ClassManager().resolve_schema_type(_address.class_name)
        except AmsdalClassError as e:
            raise ClassNotFoundError(_address.class_name) from e

        model_class = ClassManager().import_model_class(_address.class_name, schema_type)

        permissions_info = cls.get_permissions_info(model_class, user)
        class_properties = cls.get_class_properties(schema)

        result = ObjectsResponse(
            columns=class_properties,
            rows=[],
        )

        if permissions_info.has_read_permission:
            _address = apply_version_to_address(
                _address,
                version_id=version_id or _address.object_version,
                all_versions=all_versions,
            )
            qs = model_class.objects.filter(
                _metadata__is_deleted=False,
                _address__object_id=_address.object_id,
                _address__class_version=_address.class_version,
                _address__object_version=_address.object_version,
            )

            if all_versions:
                qs = qs.using(LAKEHOUSE_DB_ALIAS)

            items: list[Model] = qs.execute()

            for item in items:
                result.rows.append(
                    cls.build_object_data(
                        item,
                        include_metadata=include_metadata,
                    ),
                )

        return result
