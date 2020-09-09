# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Tuple

from flask_restful import Resource
from flasgger import swag_from

from search_service.proxy import get_proxy_client


class TestAPI(Resource):
    """
    API to test
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()

    @swag_from('swagger_doc/testsubmodule_get.yml')
    def get(self) -> Tuple[str, int]:
        return '', HTTPStatus.OK
