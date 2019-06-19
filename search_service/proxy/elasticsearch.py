import logging
import re

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, query
from flask import current_app

from search_service import config
from search_service.models.search_result import SearchResult
from search_service.models.table import Table
from search_service.proxy.base import BaseProxy
from search_service.proxy.statsd_utilities import timer_with_counter

# Default Elasticsearch index to use, if none specified
DEFAULT_ES_INDEX = 'table_search_index'

LOGGING = logging.getLogger(__name__)


class ElasticsearchProxy(BaseProxy):
    """
    ElasticSearch connection handler
    """
    def __init__(self, *,
                 host: str = None,
                 user: str = '',
                 password: str = '',
                 client: Elasticsearch = None,
                 page_size: int = 10
                 ) -> None:
        """
        Constructs Elasticsearch client for interactions with the cluster.
        Allows caller to pass a fully constructed Elasticsearch client, {elasticsearch_client}
        or constructs one from the parameters provided.

        :param host: Elasticsearch host we should connect to
        :param auth_user: user name to use for authentication
        :param auth_pw: user password to use for authentication
        :param elasticsearch_client: Elasticsearch client to use, if provided
        :param  page_size: Number of search results to return per request
        """
        if client:
            self.elasticsearch = client
        else:
            self.elasticsearch = Elasticsearch(host, http_auth=(user, password))

        self.page_size = page_size

    def _get_table_search_result(self, page_index: int,
                                 client: Search) -> SearchResult:
        """
        Common helper function to get result.

        :param page_index:
        :param client
        :return:
        """
        table_results = []
        # Use {page_index} to calculate index of results to fetch from
        start_from = page_index * self.page_size
        end_at = start_from + self.page_size
        client = client[start_from:end_at]
        response = client.execute()

        for hit in response:

            try:
                table = Table(name=hit.name,
                              key=hit.key,
                              description=hit.description,
                              cluster=hit.cluster,
                              database=hit.database,
                              schema_name=hit.schema_name,
                              column_names=hit.column_names,
                              tags=hit.tags,
                              last_updated_epoch=hit.last_updated_epoch)

                table_results.append(table)
            except Exception:
                LOGGING.exception('The record doesnt contain specified field.')
                pass

        return SearchResult(total_results=response.hits.total,
                            results=table_results)

    def _search_helper(self, query_term: str,
                       page_index: int,
                       client: Search) -> SearchResult:
        """
        Constructs Elasticsearch Query DSL to:
          1. Use function score to customize scoring of search result. It currently uses "total_usage" field to score.
          `Link https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html`_
          2. Uses multi match query to search term in multiple fields.
          `Link https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html`_

        :param query_term:
        :param page_index:
        :param client:
        :return:
        """

        if query_term:
            d = {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": query_term,
                            "fields": ["name.raw^30",
                                       "name^5",
                                       "schema_name^3",
                                       "description^3",
                                       "column_names^2",
                                       "column_descriptions", "tags"]
                        }
                    },
                    "field_value_factor": {
                        "field": "total_usage",
                        "modifier": "log1p"
                    }
                }
            }
            q = query.Q(d)
            client = client.query(q)

        return self._get_table_search_result(page_index=page_index,
                                             client=client)

    def _search_wildcard_helper(self, field_value: str,
                                page_index: int,
                                client: Search,
                                field_name: str) -> SearchResult:
        """
        Do a wildcard match search with the query term.

        :param field_value:
        :param page_index:
        :param client:
        :param field_name
        :return:
        """
        if field_value and field_name:
            d = {
                "wildcard": {
                    field_name: field_value
                }
            }
            q = query.Q(d)
            client = client.query(q)

        return self._get_table_search_result(page_index=page_index,
                                             client=client)

    @classmethod
    def _field_name_transform(cls, *, field_name: str) -> str:
        """
        ES store document with field tag_names. Convert user input to internal field name.

        :param field_name:
        :return:
        """
        if field_name == 'tag':
            field_name = 'tags'
        elif field_name == 'schema':
            field_name = 'schema_name.raw'
        elif field_name == 'table':
            field_name = 'name.raw'
        elif field_name == 'column':
            field_name = 'column_names.raw'
        return field_name

    @timer_with_counter
    def fetch_search_results_with_field(self, *,
                                        query_term: str,
                                        field_name: str,
                                        field_value: str,
                                        page_index: int = 0,
                                        index: str = '') -> SearchResult:
        """
        todo (Tao): modify the method name to fetch_table_search_results_with_field
        Query Elasticsearch and return results as list of Table objects
        In order to support search filtered by field, it uses Elasticsearch's filter.
        https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=filter#dotted-fields

        :param query_term: search query term
        :param field_name: field name to do the searching(e.g schema_name, tag_names)
        :param field_value: value for the field for filtering
        :param page_index: index of search page user is currently on
        :param index: current index for search. Provide different index for different resource.
        :return: SearchResult Object
        :return:
        """
        current_index = index if index else \
            current_app.config.get(config.ELASTICSEARCH_INDEX_KEY, DEFAULT_ES_INDEX)

        s = Search(using=self.elasticsearch, index=current_index)

        field_name = self._field_name_transform(field_name=field_name)

        # We allow user to use ? * for wildcard support
        m = re.search('[\?\*]', field_value)
        if m:
            return self._search_wildcard_helper(field_value=field_value,
                                                page_index=page_index,
                                                client=s,
                                                field_name=field_name)
        else:
            s = s.filter('term', **{field_name: field_value})
            return self._search_helper(query_term=query_term,
                                       page_index=page_index,
                                       client=s)

    @timer_with_counter
    def fetch_search_results(self, *,
                             query_term: str,
                             page_index: int = 0,
                             index: str = '') -> SearchResult:
        """
        todo (Tao): modify the method name to fetch_table_search_results
        Query Elasticsearch and return results as list of Table objects
        :param query_term: search query term
        :param page_index: index of search page user is currently on
        :param index: current index for search. Provide different index for different resource.
        :return: SearchResult Object
        """
        current_index = index if index else \
            current_app.config.get(config.ELASTICSEARCH_INDEX_KEY, DEFAULT_ES_INDEX)
        if not query_term:
            # return empty result for blank query term
            return SearchResult(total_results=0, results=[])

        s = Search(using=self.elasticsearch, index=current_index)

        return self._search_helper(query_term=query_term,
                                   page_index=page_index,
                                   client=s)

    def fetch_search_user_results(self, *,
                                  query_term: str,
                                  page_index: int = 0,
                                  index: str = '') -> SearchResult:
        pass
