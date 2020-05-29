import logging
from http import HTTPStatus
from typing import Iterable, Any

from flasgger import swag_from
from flask_restful import Resource, reqparse  # noqa: I201

from search_service.exception import NotFoundException
from search_service.models.dashboard import SearchDashboardResultSchema
from search_service.proxy import get_proxy_client


DASHBOARD_INDEX = 'dashboard_search_index'

LOGGING = logging.getLogger(__name__)


class SearchDashboardAPI(Resource):
    """
    Search Dashboard API
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=DASHBOARD_INDEX, type=str)

        super(SearchDashboardAPI, self).__init__()

    @swag_from('swagger_doc/dashboard/search_dashboard.yml')
    def get(self) -> Iterable[Any]:
        """
        Fetch dashboard search results based on query_term.

        :return: list of dashboard  results. List can be empty if query
        doesn't match any dashboards
        """
        args = self.parser.parse_args(strict=True)
        try:
            results = self.proxy.fetch_dashboard_search_results(
                query_term=args.get('query_term'),
                page_index=args['page_index'],
                index=args['index']
            )

            return SearchDashboardResultSchema().dump(results).data, HTTPStatus.OK

        except NotFoundException:
            return {'message': 'query_term does not exist'}, HTTPStatus.NOT_FOUND

        except Exception:

            err_msg = 'Exception encountered while processing search request'
            LOGGING.exception(err_msg)
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class SearchDashboardFilterAPI(Resource):
    """
    Search Dashboard API using search filtering

    This API should be generic enough to support every search filter use case.
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('index', required=False, default=DASHBOARD_INDEX, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('search_request', type=dict)

        super(SearchDashboardFilterAPI, self).__init__()

    @swag_from('swagger_doc/dashboard/search_dashboard_filter.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch search results based on the page_index, query_term, and
        search_request dictionary posted in the request JSON.

        :return: list of table results. List can be empty if query
        doesn't match any dashboard
        """
        args = self.parser.parse_args(strict=True)
        page_index = args.get('page_index')  # type: int

        search_request = args.get('search_request')  # type: Dict
        if search_request is None:
            msg = 'The search request payload is not available in the request'
            return {'message': msg}, HTTPStatus.BAD_REQUEST

        query_term = args.get('query_term')  # type: str
        if ':' in query_term:
            msg = 'The query term contains an invalid character'
            return {'message': msg}, HTTPStatus.BAD_REQUEST

        try:
            results = self.proxy.fetch_search_results_with_filter(
                query_term=query_term,
                search_request=search_request,
                page_index=page_index,
                index=args['index']
            )
            return results, HTTPStatus.OK
        except RuntimeError:
            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
