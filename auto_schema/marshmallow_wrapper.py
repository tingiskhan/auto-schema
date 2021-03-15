from sqlalchemy import Enum, LargeBinary
from sqlalchemy.sql.elements import Label
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from functools import lru_cache
from typing import Type, Dict, Any, TypeVar
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.relationships import RelationshipProperty
from marshmallow import fields as f
from .utils import find_col_types, get_columns_of_object, add_relationships
from .field_generator import EnumFieldGenerator, BytesFieldGenerator


T = TypeVar("T")


class AutoMarshmallowSchema(SQLAlchemyAutoSchema):
    LOAD_ONLY_FIELDS = "load_only_fields"
    CUSTOM_HANDLERS = {Enum: EnumFieldGenerator(), LargeBinary: BytesFieldGenerator()}

    @classmethod
    @lru_cache(maxsize=100)
    def generate_schema(cls, base_class: Type[DeclarativeMeta]) -> Type["AutoMarshmallowSchema"]:
        state_dict = {"Meta": type("Meta", (object,), {"model": base_class, "include_fk": True})}

        cls._handle_custom(base_class, state_dict)
        cls._handle_label_fields(base_class, state_dict)
        cls._handle_relationships(base_class, state_dict)

        return type(f"{base_class.__name__}Schema", (AutoMarshmallowSchema,), state_dict)

    @staticmethod
    def _create_key_as_type(key, state_dict, type_):
        if key not in state_dict:
            state_dict[key] = type_()

    @classmethod
    def _handle_custom(cls, base_class: Type[DeclarativeMeta], state_dict: Dict[str, Any]):
        for column_type, handler in cls.CUSTOM_HANDLERS.items():
            columns_of_type = find_col_types(base_class, column_type)

            for column in columns_of_type:
                handler(column, state_dict)

    @classmethod
    def _handle_label_fields(cls, base_class: Type[DeclarativeMeta], state_dict: Dict[str, Any]):
        for column in get_columns_of_object(base_class):
            if not isinstance(column.property.expression, Label):
                continue

            cls._create_key_as_type(cls.LOAD_ONLY_FIELDS, state_dict, list)
            state_dict[cls.LOAD_ONLY_FIELDS] += [column.name]

    @classmethod
    def _handle_relationships(cls, base_class: Type[DeclarativeMeta], state_dict: Dict[str, Any]):
        for relship in get_columns_of_object(base_class, RelationshipProperty):
            rel_schema = AutoMarshmallowSchema.generate_schema(relship.property.mapper.class_)

            state_dict[relship.key] = f.Nested(rel_schema, many=relship.property.uselist)

            cls._create_key_as_type(cls.LOAD_ONLY_FIELDS, state_dict, list)
            state_dict[cls.LOAD_ONLY_FIELDS] += [relship.key]

    @classmethod
    def get_schema(cls, obj: Type):
        return cls.generate_schema(obj)

    @classmethod
    def get_subclasses(cls, base):
        res = base.__subclasses__()

        for e in res:
            res.extend(cls.get_subclasses(e))

        return res

    def load_instance(self, objects: T, **kwargs) -> T:
        relation_columns = tuple(get_columns_of_object(self.Meta.model, RelationshipProperty))
        deserialized = self.load(objects, **kwargs)

        is_list = True
        if isinstance(deserialized, dict):
            deserialized = [deserialized]
            is_list = False

        res = list()
        for r in deserialized:
            rels = dict()
            for relation_column in relation_columns:
                popped = r.pop(relation_column.key, None)
                if popped is None:
                    continue

                rels[relation_column.key] = add_relationships(relation_column, popped)

            r.update(rels)
            obj = self.Meta.model(**r)

            res.append(obj)

        if is_list:
            return res

        return res[0]