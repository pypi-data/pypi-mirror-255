from amsdal.configs.main import settings
from amsdal.migration.manager import MigrationManager
from amsdal.schemas.manager import SchemaManager
from amsdal_data.table_schemas.manager import TableSchemasManager
from amsdal_models.classes.constants import USER_MODELS_MODULE
from amsdal_models.classes.data_models.dependencies import DependencyModelNames
from amsdal_models.classes.manager import ClassManager
from amsdal_models.classes.model import Model
from amsdal_models.classes.utils import resolve_base_class_for_schema
from amsdal_models.classes.writer import ClassWriter
from amsdal_models.enums import MetaClasses
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS
from amsdal_models.schemas.data_models.schema import ObjectSchema
from amsdal_models.schemas.data_models.schema import PropertyData
from amsdal_models.schemas.manager import BuildSchemasManager
from amsdal_utils.models.enums import SchemaTypes
from amsdal_utils.models.enums import Versions
from starlette.authentication import BaseUser

from amsdal_server.apps.classes.errors import ClassNotFoundError
from amsdal_server.apps.classes.mixins.column_info_mixin import ColumnInfoMixin
from amsdal_server.apps.classes.mixins.model_class_info import ModelClassMixin
from amsdal_server.apps.classes.serializers.class_info import ClassInfo
from amsdal_server.apps.classes.serializers.register_class import ClassSchema
from amsdal_server.apps.classes.serializers.register_class import RegisterClassData
from amsdal_server.apps.common.errors import AmsdalPermissionError
from amsdal_server.apps.common.mixins.permissions_mixin import PermissionsMixin
from amsdal_server.apps.common.permissions.enums import AccessTypes
from amsdal_server.apps.objects.mixins.object_data_mixin import ObjectDataMixin


class ClassesApi(PermissionsMixin, ModelClassMixin, ColumnInfoMixin, ObjectDataMixin):
    @classmethod
    def get_classes(cls, user: BaseUser) -> list[ClassInfo]:
        classes: list[Model] = cls.get_class_objects_qs().execute()
        result: list[ClassInfo] = []
        schema_manager = SchemaManager()

        for class_item in classes:
            schema = schema_manager.get_schema_by_name(class_item.title)  # type: ignore[attr-defined]

            if not schema:
                class_name = class_item.title  # type: ignore[attr-defined]
                raise ClassNotFoundError(class_name, f'Class not found: "{class_name}"')

            if schema.meta_class == MetaClasses.TYPE:
                continue

            result.append(cls.get_class(user, class_item))

        return result

    @classmethod
    def get_class_by_name(
        cls,
        user: BaseUser,
        class_name: str,
    ) -> ClassInfo:
        class_item: Model | None = cls.get_class_objects_qs().filter(title=class_name).first().execute()

        if not class_item:
            msg = f'Class not found: {class_name}'
            raise ClassNotFoundError(class_name, msg)

        return cls.get_class(user, class_item)

    @classmethod
    def get_class(
        cls,
        user: BaseUser,
        class_item: Model,
    ) -> ClassInfo:
        model_class = cls.get_model_class(class_item)
        permissions_info = cls.get_permissions_info(model_class, user)
        class_properties = cls.get_class_properties_by_class_name(class_item.title)  # type: ignore[attr-defined]
        class_info = ClassInfo(
            **{
                'class': class_item.title,  # type: ignore[attr-defined]
                'count': 0,
                'properties': class_properties,
            },
        )

        if permissions_info.has_read_permission:
            class_info.count = len(
                model_class.objects.filter(
                    _metadata__is_deleted=False,
                    _address__class_version=Versions.LATEST,
                    _address__object_version=Versions.LATEST,
                ).execute()
            )

        return class_info

    @classmethod
    def register_class(
        cls,
        user: BaseUser,
        data: RegisterClassData,
        *,
        skip_data_migrations: bool = False,
    ) -> ClassInfo:
        from models.core.class_object import ClassObject  # type: ignore[import-not-found]

        permissions_info = cls.get_permissions_info(
            ClassObject,
            user,
            [AccessTypes.CREATE, AccessTypes.UPDATE],
        )
        object_schema = cls._build_object_schema(data.class_schema)

        model_object = (
            ClassObject.objects.using(LAKEHOUSE_DB_ALIAS)
            .filter(
                _address__object_version=Versions.LATEST,
                _metadata__is_deleted=False,
                title=data.class_schema.title,
            )
            .first()
            .execute()
        )

        if model_object:
            if not permissions_info.has_update_permission:
                raise AmsdalPermissionError(
                    access_type=AccessTypes.UPDATE,
                    class_name=ClassObject.__name__,
                )
        elif not permissions_info.has_create_permission:
            raise AmsdalPermissionError(
                access_type=AccessTypes.CREATE,
                class_name=ClassObject.__name__,
            )

        cls._generate_model_class(object_schema)
        cls._migrate_model(object_schema, skip_data_migrations=skip_data_migrations)

        class_properties = cls.get_class_properties(object_schema)
        class_info = ClassInfo(
            **{  # type: ignore[arg-type]
                'class': object_schema.title,
                'count': 0,  # TODO: get count
                'properties': class_properties,
            },
        )

        return class_info

    @classmethod
    def unregister_class(
        cls,
        user: BaseUser,
        class_name: str,
    ) -> None:
        from models.core.class_object import ClassObject

        permissions_info = cls.get_permissions_info(
            ClassObject,
            user,
            [AccessTypes.DELETE],
        )

        if not permissions_info.has_update_permission:
            raise AmsdalPermissionError(
                access_type=AccessTypes.DELETE,
                class_name=ClassObject.__name__,
            )

        class_object = (
            ClassObject.objects.filter(
                title=class_name,
                _metadata__is_deleted=False,
                _address__object_version=Versions.LATEST,
            )
            .first()
            .execute()
        )

        if class_object:
            class_object.get_metadata().is_deleted = True
            class_object.save()

    @classmethod
    def _build_object_schema(cls, class_schema: ClassSchema) -> ObjectSchema:
        return ObjectSchema(  # type: ignore[call-arg]
            title=class_schema.title,
            type=class_schema.type,
            properties={
                property_name: PropertyData(**property_data.model_dump())
                for property_name, property_data in class_schema.properties.items()
            },
            required=class_schema.required,
            indexed=class_schema.indexed,
            unique_properties=class_schema.unique,
            custom_code=class_schema.custom_code,
        )

    @classmethod
    def _generate_model_class(cls, schema: ObjectSchema) -> None:
        model_names = DependencyModelNames.build_from_database()
        class_writer = ClassWriter(settings.models_root_path)
        class_writer.generate_model(
            schema=schema,
            schema_type=SchemaTypes.USER,
            base_class=resolve_base_class_for_schema(schema),
            model_names=model_names,
            sub_models_directory=USER_MODELS_MODULE,
        )

        class_manager = ClassManager()
        class_manager.init_models_root(settings.models_root_path)
        class_manager.unload_classes(schema.title, SchemaTypes.USER)
        BuildSchemasManager.add_user_schema(settings.schemas_root_path, schema)
        schema_manager = SchemaManager()
        schema_manager.invalidate_user_schemas()

    @classmethod
    def _migrate_model(cls, schema: ObjectSchema, *, skip_data_migrations: bool = False) -> None:
        from models.core.class_object import ClassObject

        class_manager = ClassManager()
        migration_manager = MigrationManager(
            schema_manager=SchemaManager(),
            table_schema_manager=TableSchemasManager(),
            class_manager=class_manager,
        )

        migration_manager.migrate_class(
            object_schema=schema,
            base_class=ClassObject,
            schema_type=SchemaTypes.USER,
            skip_data_migrations=skip_data_migrations,
        )
