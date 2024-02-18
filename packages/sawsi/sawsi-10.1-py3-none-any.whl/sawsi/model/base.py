from pydantic import BaseModel
from typing import TypeVar, Generic, Type


# 현재 클래스 형을 나타내는 TypeVar 생성
T = TypeVar('T', bound='DynamoModel')

class DynamoModel(BaseModel, Generic[T]):
    @classmethod
    def _table_name(cls):
        return cls._table.get_default()

    @classmethod
    def _get_type(cls, field_name):
        street_field_info = cls.model_fields[field_name]
        if street_field_info.annotation == str:
            return 'S'
        elif street_field_info.annotation == float:
            return 'N'
        elif street_field_info.annotation == int:
            return 'N'
        elif street_field_info.annotation == bytes:
            return 'B'
        raise ValueError(f'Cannot make index type "{field_name}"')

    @classmethod
    def get_item(cls: Type[T], id: str, consistent_read: bool = True) -> T:
        data = cls.__dynamo__.get_item(
            cls._table_name(), id, consistent_read
        )
        return cls(**data)

    @classmethod
    def sync_table(cls):
        """
        테이블이 없으면 생성, 인덱스도 없으면 생성합니다.
        :return:
        """
        cls.__dynamo__.create_table(cls._table_name())
        for partition_key, sort_key in cls._indexes.get_default():
            partition_key_type = cls._get_type(partition_key)
            if sort_key:
                sort_key_type = cls._get_type(sort_key)
                cls.__dynamo__.create_global_index(
                    cls._table_name(),
                    partition_key, partition_key_type,
                    sort_key, sort_key_type
                )
            else:
                cls.__dynamo__.create_global_index(
                    cls._table_name(),
                    partition_key, partition_key_type,
                )

