import unittest

from mock import patch

from search_service.api.table import SearchTableQueryStringAPI
from search_service import create_app


class SearchStringQueryTableAPITest(unittest.TestCase):
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
        RequestParser().parse_args.return_value = dict(query_term='hello',
                                                       index='fake_index',
                                                       page_index=0)
        SearchTableQueryStringAPI().get()
        mock_proxy.fetch_string_query_search_results.assert_called_with(query_string='hello',
                                                                        index='fake_index',
                                                                        page_index=0)
