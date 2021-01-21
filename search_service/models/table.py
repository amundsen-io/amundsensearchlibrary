# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Set

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema

from .base import Base
from search_service.models.tag import Tag
import time

@attr.s(auto_attribs=True, kw_only=True)
class Table(Base):
    """
    This represents the part of a table stored in the search proxy
    """
    id: str
    database: Optional[str] = None
    cluster: Optional[str] = None
    schema: Optional[str] = None
    name: Optional[str] = None
    key: Optional[str] = None
    display_name: Optional[str] = None
    tags: List[Tag] = []
    badges: List[Tag] = []
    description: Optional[str] = None
    last_updated_timestamp: int = int(time.time())
    # The following properties are lightly-transformed properties from the normal table object:
    column_names: List[str] = []
    column_descriptions: List[str] = []
    programmatic_descriptions: List[str] = []
    # The following are search-only properties:
    total_usage: int = 0
    schema_description: Optional[str] = attr.ib(default=None)

    def get_id(self) -> str:
        return self.id

    def get_attrs_dict(self) -> dict:
        attrs_dict = self.__dict__.copy()
        attrs_dict['tags'] = [str(tag) for tag in self.tags]
        attrs_dict['badges'] = [str(tag) for tag in self.badges]
        return attrs_dict

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'id',
            'name',
            'key',
            'description',
            'cluster',
            'database',
            'schema',
            'column_names',
            'tags',
            'badges',
            'last_updated_timestamp',
            'display_name',
            'programmatic_descriptions',
            'total_usage',
            'schema_description'
        }

    @staticmethod
    def get_type() -> str:
        return 'table'


class TableSchema(AttrsSchema):
    class Meta:
        target = Table
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class SearchTableResult:
    total_results: int = attr.ib()
    results: List[Table] = attr.ib(factory=list)


class SearchTableResultSchema(AttrsSchema):
    class Meta:
        target = SearchTableResult
        register_as_scheme = True
