import unittest

from http import HTTPStatus
from mock import patch, Mock

from search_service.api.document import CleanDocumentAPI
from search_service import create_app


class CleanDocumentAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.Config')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tear_down(self):
        self.app_context.pop()

    @patch('search_service.api.document.reqparse.RequestParser')
    @patch('search_service.api.document.get_proxy_client')
    def test_put(self, get_proxy, RequestParser) -> None:
        mock_proxy = get_proxy.return_value = Mock()
        RequestParser().parse_args.return_value = dict(index='fake_index')

        response = CleanDocumentAPI().put()
        self.assertEqual(list(response)[1], HTTPStatus.OK)
        mock_proxy.clean_documents.assert_called_once_with(before=None, index='fake_index')
