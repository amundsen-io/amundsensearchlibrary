from luqum.utils import LuceneTreeTransformer
from luqum.parser import parser
from luqum.tree import UnknownOperation, SearchField, Word
from typing import List, Optional, Union


class QueryTransformer(LuceneTreeTransformer):
    """
    QueryTransformer uses the LuceneTreeTransformer to modify the query tree in place

    The NAME_MAPPING values come from the table schema defined in index_map.py
    """
    NAME_MAPPING = {
        'tag': 'tags',
        'schema': 'schema_name.raw',
        'table': 'name.raw',
        'column': 'column_names.raw',
        'database': 'database',
        'description': 'description'
    }

    VALUE_MAPPING = {
        'schema_name.raw': '^3',
        'name.raw': '^30',
        'column_names.raw': '^2',
        'description': '^3'
    }

    def visit_search_field(self, node: SearchField, parents: List[UnknownOperation]) -> SearchField:
        """
        Built-in method called when the parser visits a search field node. This
        method maps user input to elasticsearch mapping (as defined in index_map.py)
        """
        mapped: Optional[str] = self.NAME_MAPPING.get(node.name)
        if mapped is not None:
            node.name = mapped
        return node

    def visit_term(self, node: Word, parents: List[Union[SearchField, UnknownOperation]]) -> Word:
        """
        Built-in method called when the parser visits some user supplied input that
        is not a search field.
        """
        if not parents:
            return node

        # The immediate parent of our node is the last element in the list
        parent = parents[-1]

        # if the parent isn't a search field, we can return early
        if not type(parent) == SearchField:
            return node

        if parent.name == '_exists_':
            # if the user supplies "_exists_:some_value", we want to map "some_value"
            # to its proper name in the elasticsearch schema
            node.value = self.NAME_MAPPING.get(node.value, node.value)
        else:
            # Boost some search field values higher than others
            boost = self.VALUE_MAPPING.get(parent.name, '')
            node.value = f'{node.value}{boost}'
        return node

    def parse(self, *, query: str) -> str:
        parsed_query: UnknownOperation = parser.parse(query)
        QueryTransformer().visit(parsed_query)
        return str(parsed_query)
