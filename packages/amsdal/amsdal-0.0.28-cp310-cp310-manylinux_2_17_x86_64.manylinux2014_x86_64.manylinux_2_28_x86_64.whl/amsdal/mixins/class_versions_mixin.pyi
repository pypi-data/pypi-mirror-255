from amsdal.migration.utils import object_schema_to_table_schema as object_schema_to_table_schema
from amsdal_models.classes.model import Model

class ClassVersionsMixin:
    @classmethod
    def _create_table(cls, schema_object: Model) -> None: ...
    @classmethod
    def init_class_versions(cls, *, create_tables: bool = False) -> None: ...
    @staticmethod
    def register_internal_classes() -> None: ...
