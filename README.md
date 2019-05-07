# Amundsen Search service
[![PyPI version](https://badge.fury.io/py/amundsen-search.svg)](https://badge.fury.io/py/amundsen-search)
[![Build Status](https://api.travis-ci.com/lyft/amundsensearchlibrary.svg?branch=master)](https://travis-ci.com/lyft/amundsensearchlibrary)
[![Coverage Status](https://img.shields.io/codecov/c/github/lyft/amundsensearchlibrary/master.svg)](https://codecov.io/github/lyft/amundsensearchlibrary?branch=master)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://bit.ly/2FVq37z)

Amundsen Search service serves a Restful API and is responsible for searching metadata. The service leverages [Elasticsearch](https://www.elastic.co/products/elasticsearch "Elasticsearch") for most of it's search capabilites.

## Instructions to start the Search service from distribution
```bash
$ venv_path=[path_for_virtual_environment]
$ python3 -m virtualenv $venv_path
$ source $venv_path/bin/activate
$ pip3 install amundsensearch
$ python3 search_service/search_wsgi.py
```

In a different terminal, verify the service is up by running
```bash
$ curl -v http://localhost:5000/healthcheck
```

## Instructions to start the Search service from the source
```bash
$ git clone https://github.com/lyft/amundsensearchlibrary.git
$ cd amundsensearchlibrary
$ venv_path=[path_for_virtual_environment]
$ python3 -m virtualenv $venv_path
$ source $venv_path/bin/activate
$ pip3 install -r requirements.txt
$ python3 setup.py install
$ python3 search_service/search_wsgi.py
```

In different terminal, verify the service is up by running
```bash
$ curl -v http://localhost:5000/healthcheck
```

## Instructions to start the service from the Docker
```bash
$ docker pull amundsendev/amundsen-search:latest
$ docker run -p 5000:5000 amundsendev/amundsen-search
```

In different terminal, verify the service is up by running
```bash
$ curl -v http://localhost:5000/healthcheck
```

## Production environment
By default, Flask comes with a Werkzeug webserver, which is used for development. For production environments a production grade web server such as [Gunicorn](https://gunicorn.org/ "Gunicorn") should be used.

```bash
$ pip3 install gunicorn
$ gunicorn search_service.search_wsgi
```

In different terminal, verify the service is up by running
```bash
$ curl -v http://localhost:8000/healthcheck
```
For more imformation see the [Gunicorn configuration documentation](http://docs.gunicorn.org/en/latest/run.html "documentation").

### Configuration outside local environment
By default, Search service uses [LocalConfig](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/config.py "LocalConfig") that looks for Elasticsearch running in localhost.
In order to use different end point, you need to create a [Config](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/config.py "Config") suitable for your use case. Once a config class has been created, it can be referenced by an [environment variable](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/search_wsgi.py "environment variable"): `SEARCH_SVC_CONFIG_MODULE_CLASS`

For example, in order to have different config for production, you can inherit Config class, create Production config and passing production config class into environment variable. Let's say class name is ProdConfig and it's in search_service.config module. then you can set as below:

`SEARCH_SVC_CONFIG_MODULE_CLASS=search_service.config.ProdConfig`

This way Search service will use production config in production environment. For more information on how the configuration is being loaded and used, here's reference from Flask [doc](http://flask.pocoo.org/docs/1.0/config/#development-production "doc").

# Developer guide
## Code style
- PEP 8: Amundsen Search service follows [PEP8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/ "PEP8 - Style Guide for Python Code"). 
- Typing hints: Amundsen Search service also utilizes [Typing hint](https://docs.python.org/3/library/typing.html "Typing hint") for better readability.

## Code structure
Amundsen Search service consists of three packages, API, Models, and Proxy.

### [API package](https://github.com/lyft/amundsensearchlibrary/tree/master/search_service/api "API package")
A package that contains [Flask Restful resources](https://flask-restful.readthedocs.io/en/latest/api.html#flask_restful.Resource "Flask Restful resources") that serves Restful API request.
The [routing of API](https://flask-restful.readthedocs.io/en/latest/quickstart.html#resourceful-routing "routing of API") is being registered [here](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/__init__.py "here").

### [Proxy package](https://github.com/lyft/amundsensearchlibrary/tree/master/search_service/proxy "Proxy package")
Proxy package contains proxy modules that talks dependencies of Search service. There are currently two modules in Proxy package, [Elasticsearch](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/proxy/elasticsearch.py "Elasticsearch") and [Statsd](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/proxy/statsd_utilities.py "Statsd").

##### [Elasticsearch proxy module](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/proxy/elasticsearch.py "Elasticsearch proxy module")
[Elasticsearch](https://www.elastic.co/products/elasticsearch "Elasticsearch") proxy module serves various use case of searching metadata from Elasticsearch. It uses [Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html "Query DSL") for the use case, execute the search query and transform into [model](https://github.com/lyft/amundsensearchlibrary/tree/master/search_service/models "model").

##### [Statsd utilities module](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/proxy/statsd_utilities.py "Statsd utilities module")
[Statsd](https://github.com/etsy/statsd/wiki "Statsd") utilities module has methods / functions to support statsd to publish metrics. By default, statsd integration is disabled and you can turn in on from [Search service configuration](https://github.com/lyft/amundsensearchlibrary/blob/master/search_service/config.py#L7 "Search service configuration").
For specific configuration related to statsd, you can configure it through [environment variable.](https://statsd.readthedocs.io/en/latest/configure.html#from-the-environment "environment variable.")

### [Models package](https://github.com/lyft/amundsensearchlibrary/tree/master/search_service/models "Models package")
Models package contains many modules where each module has many Python classes in it. These Python classes are being used as a schema and a data holder. All data exchange within Amundsen Search service use classes in Models to ensure validity of itself and improve readability and maintainability.

