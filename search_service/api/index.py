import logging

from flasgger import swag_from
from http import HTTPStatus
from typing import Tuple, Any
from flask_restful import Resource

from search_service.proxy import get_proxy_client
from search_service.api.table import TABLE_INDEX

LOGGER = logging.getLogger(__name__)


class IndexAPI(Resource):

    def __init__(self) -> None:
        self.proxy = get_proxy_client()
        super(IndexAPI, self).__init__()

    @swag_from('swagger_doc/index/index_delete.yml')
    def delete(self, *, index: str = TABLE_INDEX) -> Tuple[Any, int]:
        """
        Deletes the specified Elasticsearch index

        :param index: alias or id for the index that should be deleted
        :return:
        """
        try:
            self.proxy.delete_index(index=index)
            return {}, HTTPStatus.OK
        except RuntimeError:
            err_msg = 'Exception encountered while deleting index'
            LOGGER.exception(err_msg)
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
