import unittest

from http import HTTPStatus
from mock import patch, Mock

from search_service.api.index import IndexAPI
from search_service import create_app


class IndexAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tear_down(self):
        self.app_context.pop()

    @patch('search_service.api.index.get_proxy_client')
    def test_delete(self, get_proxy) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        response = IndexAPI().delete(index='fake_index')
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.delete_index.assert_called_with(index='fake_index')
