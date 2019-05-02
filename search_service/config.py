import os

ELASTICSEARCH_ENDPOINT_KEY = 'ELASTICSEARCH_ENDPOINT'
ELASTICSEARCH_INDEX_KEY = 'ELASTICSEARCH_INDEX'
ELASTICSEARCH_AUTH_USER_KEY = 'ELASTICSEARCH_AUTH_USER'
ELASTICSEARCH_AUTH_PW_KEY = 'ELASTICSEARCH_AUTH_PW'
ELASTICSEARCH_CLIENT_KEY = 'ELASTICSEARCH_CLIENT'
SEARCH_PAGE_SIZE_KEY = 'SEARCH_PAGE_SIZE'
STATS_FEATURE_KEY = 'STATS'

PROXY_ENDPOINT = 'PROXY_ENDPOINT'
PROXY_USER = 'PROXY_USER'
PROXY_PASSWORD = 'PROXY_PASSWORD'
PROXY_CLIENT = 'PROXY_CLIENT'
PROXY_CLIENTS = {
    'ELASTICSEARCH': 'search_service.proxy.elasticsearch.ElasticsearchProxy',
}


class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:' \
                 '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    STATS = False
    LOCAL_HOST = '0.0.0.0'
    PROXY_PORT = '9200'
    PROXY_ENDPOINT = os.environ.get('PROXY_ENDPOINT',
                                    'http://{LOCAL_HOST}:{PORT}'.format(
                                        LOCAL_HOST=LOCAL_HOST,
                                        PORT=PROXY_PORT)
                                    )
    PROXY_CLIENT = PROXY_CLIENTS[os.environ.get('PROXY_CLIENT', 'ELASTICSEARCH')]
    PROXY_USER = os.environ.get('CREDENTIALS_PROXY_USER', 'elastic')
    PROXY_PASSWORD = os.environ.get('CREDENTIALS_PROXY_PASSWORD', 'elastic')
