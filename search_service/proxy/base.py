from abc import ABCMeta, abstractmethod
from typing import List, Union

from search_service.models.dashboard import SearchDashboardResult
from search_service.models.table import SearchTableResult
from search_service.models.search_result import SearchResult
from search_service.models.table import Table, TableSchema
from search_service.models.user import User, UserSchema


class BaseProxy(metaclass=ABCMeta):
    """
    Base Proxy, which behaves like an interface for all
    the proxy clients available in the amundsen search service
    """

    @abstractmethod
    def fetch_table_search_results(self, *,
                                   query_term: str,
                                   page_index: int = 0,
                                   index: str = '') -> SearchTableResult:
        pass

    @abstractmethod
    def fetch_user_search_results(self, *,
                                  query_term: str,
                                  page_index: int = 0,
                                  index: str = '') -> SearchResult:
        pass

    @abstractmethod
    def update_document(self, *,
                        data: List[Union[Table, User]] = [],
                        index: str = '',
                        schema: Union[TableSchema, UserSchema]) -> str:
        pass

    @abstractmethod
    def create_document(self, *,
                        data: List[Union[Table, User]] = [],
                        index: str = '',
                        schema: Union[TableSchema, UserSchema]) -> str:
        pass

    @abstractmethod
    def delete_document(self, *,
                        data: List[str],
                        index: str = '') -> str:
        pass

    @abstractmethod
    def fetch_table_search_results_with_filter(self, *,
                                               query_term: str,
                                               search_request: dict,
                                               page_index: int = 0,
                                               index: str = '') -> SearchTableResult:
        pass

    @abstractmethod
    def fetch_dashboard_search_results(self, *,
                                       query_term: str,
                                       page_index: int = 0,
                                       index: str = '') -> SearchDashboardResult:
        pass
