import unittest

from search_service.utils.query_transformer import QueryTransformer


class QueryTransformerTest(unittest.TestCase):
    def test_parser_simple(self) -> None:
        result = QueryTransformer().parse(query='column:hello')
        self.assertEqual(result, 'column_names.raw:hello^2')

    def test_parser_simple_or(self) -> None:
        result = QueryTransformer().parse(query='(test1) or (test2)')
        self.assertEqual(result, '(test1) or (test2)')

    def test_parser_multi(self) -> None:
        result = QueryTransformer().parse(query='table:test1 table:test2')
        self.assertEqual(result, 'name.raw:test1^30 name.raw:test2^30')

    def test_parser_multi_or(self) -> None:
        result = QueryTransformer().parse(query='table:test1 or table:test2')
        self.assertEqual(result, 'name.raw:test1^30 or name.raw:test2^30')

    def test_parser_multi_and(self) -> None:
        result = QueryTransformer().parse(query='table:test1 and column:id')
        self.assertEqual(result, 'name.raw:test1^30 and column_names.raw:id^2')

    def test_parser_exists(self) -> None:
        result = QueryTransformer().parse(query='_exists_:table')
        self.assertEqual(result, '_exists_:name.raw')
