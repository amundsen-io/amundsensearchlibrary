import logging

from http import HTTPStatus
from typing import Tuple, Any

from flask_restful import Resource, reqparse
from search_service.proxy import get_proxy_client
from search_service.proxy.base import BaseProxy
from search_service.models.table import TableSchema
from search_service.models.user import UserSchema
from search_service.api.table import TABLE_INDEX
from search_service.api.user import USER_INDEX

LOGGER = logging.getLogger(__name__)


class BaseDocumentAPI(Resource):
    def __init__(self, schema: Any, proxy: BaseProxy) -> None:
        self.schema = schema
        self.proxy = proxy
        self.parser = reqparse.RequestParser(bundle_errors=True)
        super(BaseDocumentAPI, self).__init__()

    def delete(self, *, document_id: str) -> Tuple[Any, int]:
        """
        Uses the Elasticsearch bulk API to delete existing documents by id

        :param document_id: document id for document to be deleted
        :return:
        """
        args = self.parser.parse_args()

        try:
            self.proxy.delete_document(data=[document_id], index=args.get('index'))
            return {}, HTTPStatus.OK
        except RuntimeError as e:
            err_msg = 'Exception encountered while deleting document '
            LOGGER.error(err_msg + str(e))
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class DocumentTableAPI(BaseDocumentAPI):

    def __init__(self) -> None:
        super().__init__(schema=TableSchema, proxy=get_proxy_client())
        self.parser.add_argument('index', required=False, default=TABLE_INDEX, type=str)


class DocumentUserAPI(BaseDocumentAPI):

    def __init__(self) -> None:
        super().__init__(schema=UserSchema, proxy=get_proxy_client())
        self.parser.add_argument('index', required=False, default=USER_INDEX, type=str)
