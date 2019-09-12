from http import HTTPStatus
from unittest import TestCase

from mock import patch, Mock
from search_service.models.search_result import SearchResult

from search_service import create_app
from tests.unit.api.constants import get_search_result_data


class TestSearchTableFieldAPI(TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_module_class='search_service.config.Config')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.mock_client = patch('search_service.api.table.get_proxy_client')
        self.mock_proxy = self.mock_client.start().return_value = Mock()

    def tear_down(self):
        self.app_context.pop()
        self.mock_client.stop()

    def test_should_get_result_for_search(self) -> None:
        result = get_search_result_data()
        self.mock_proxy.fetch_table_search_results_with_field.return_value = \
            SearchResult(total_results=1, results=[result])

        response = self.app.test_client().get('/search/field/field_name/field_val/myvalue')

        expected_response = {
            "total_results": 1,
            "results": [result]
        }
        self.assertEqual(response.json, expected_response)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.mock_proxy.fetch_table_search_results_with_field.assert_called_with(
            query_term=None,
            field_name='field_name',
            field_value='myvalue',
            page_index=0,
            index='table_search_index'
        )

    def test_should_get_result_for_search_with_query_params(self) -> None:
        result = get_search_result_data()
        self.mock_proxy.fetch_table_search_results_with_field.return_value = \
            SearchResult(total_results=1, results=[result])

        response = self.app.test_client()\
            .get('/search/field/field_name/field_val/myvalue?query_term=hello&page_index=3')

        expected_response = {
            "total_results": 1,
            "results": [result]
        }
        self.assertEqual(response.json, expected_response)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.mock_proxy.fetch_table_search_results_with_field.assert_called_with(
            query_term='hello',
            field_name='field_name',
            field_value='myvalue',
            page_index=3,
            index='table_search_index'
        )

    def test_should_ignore_extra_search_results(self) -> None:
        search_result_with_extra_term = get_search_result_data()
        search_result_with_extra_term['extra_term'] = 'should_ignore'
        self.mock_proxy.fetch_table_search_results_with_field.return_value = \
            SearchResult(total_results=1, results=[search_result_with_extra_term])

        response = self.app.test_client().get('/search/field/field_name/field_val/myvalue')

        search_result_without_extra_term = get_search_result_data()
        expected_response = {
            "total_results": 1,
            "results": [search_result_without_extra_term]
        }
        self.assertEqual(response.json, expected_response)

    def test_should_fail_when_proxy_fails(self) -> None:
        self.mock_proxy.fetch_table_search_results_with_field.side_effect = RuntimeError('search failed')

        response = self.app.test_client().get('/search/field/field_name/field_val/myvalue')

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
