from http import HTTPStatus
from typing import Iterable, Any

from flask_restful import Resource, fields, marshal_with, reqparse

from search_service.proxy import get_proxy_client

table_fields = {
    "name": fields.String,
    "key": fields.String,
    # description can be empty, if no description is present in DB
    "description": fields.String,
    "cluster": fields.String,
    "database": fields.String,
    "schema_name": fields.String,
    "column_names": fields.List(fields.String),
    # tags can be empty list
    "tags": fields.List(fields.String),
    # last etl timestamp as epoch
    "last_updated_epoch": fields.Integer,
}

search_table_results = {
    "total_results": fields.Integer,
    "results": fields.Nested(table_fields, default=[])
}

TABLE_INDEX = 'table_search_index'


class SearchTableAPI(Resource):
    """
    Search Table API
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)

        super(SearchTableAPI, self).__init__()

    @marshal_with(search_table_results)
    def get(self) -> Iterable[Any]:
        """
        Fetch search results based on query_term.
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)

        try:

            results = self.proxy.fetch_table_search_results(
                query_term=args['query_term'],
                page_index=args['page_index'],
                index=args['index']
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class SearchTableFieldAPI(Resource):
    """
    Search Table API with explict field
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)

        # For multi field search
        self.parser.add_argument('column', required=False, default=None, action='append')
        self.parser.add_argument('table', required=False, default=None, action='append')
        self.parser.add_argument('database', required=False, default=None, action='append')
        self.parser.add_argument('schema', required=False, default=None, action='append')
        super(SearchTableFieldAPI, self).__init__()

    @marshal_with(search_table_results)
    def get(self, *, field_name: str,
            field_value: str) -> Iterable[Any]:
        """
        Fetch search results based on query_term.

        :param field_name: which field we should search from(schema, tag, table)
        :param field_value: the value to search for the field
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)

        try:
            results = self.proxy.fetch_table_search_results_with_field(
                query_term=args.get('query_term', ''),
                field_name=field_name,
                field_value=field_value,
                page_index=args['page_index'],
                index=args.get('index')
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class SearchTableMultiFieldsAPI(Resource):
    """
    Search Table API with multiple fields
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)

        # For multi field search
        self.parser.add_argument('column', required=False, default=None, action='append')
        self.parser.add_argument('table', required=False, default=None, action='append')
        self.parser.add_argument('database', required=False, default=None, action='append')
        self.parser.add_argument('schema', required=False, default=None, action='append')
        super(SearchTableMultiFieldsAPI, self).__init__()

    @marshal_with(search_table_results)
    def get(self) -> Iterable[Any]:
        """
        Return a list of results based on different matching criterias

        e.g: col:col1 && col:col2 or col:col1 && tab:tab1

        :return: A list of tables which matches the criterias.
        """
        args = self.parser.parse_args(strict=True)
        table_filters = {

        }

        if args.get('column'):
            table_filters['column'] = args.get('column')
        if args.get('table'):
            table_filters['table'] = args.get('table')
        if args.get('schema'):
            table_filters['schema'] = args.get('schema')
        if args.get('database'):
            table_filters['database'] = args.get('database')

        try:
            results = self.proxy.fetch_table_search_results_with_multi_fields(
                multi_fields=table_filters,
                page_index=args['page_index'],
                index=args.get('index')
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
