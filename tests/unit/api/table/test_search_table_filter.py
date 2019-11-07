import json
import unittest

from mock import patch

from search_service import create_app


class SearchTableFilterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tear_down(self):
        self.app_context.pop()

    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.table.get_proxy_client')
    def test_get(self, get_proxy, RequestParser) -> None:
        mock_proxy = get_proxy()
        mock_proxy.fetch_string_query_search_results.return_value = {}
        RequestParser().parse_args.return_value = dict(index='fake_index',
                                                       page_index=0)
        url = '/search/query_filter'
        self.app.test_client().get(url, json=json.dumps({'search_request': {}}))
        mock_proxy.fetch_table_search_results_with_filter.assert_called_with(index='fake_index',
                                                                             page_index=0,
                                                                             search_request={})
