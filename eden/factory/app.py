#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/eden/license

import os
import importlib
import jinja2
import eve
import eden.factory.settings
from eve.io.mongo import MongoJSONEncoder
from eve.render import send_response
from eden.celery_app import init_celery
from raven.contrib.flask import Sentry
from eden.errors import EdenError, EdenApiError
from eden.validator import EdenValidator


def configure_logging(app):
    if app.config['DEBUG'] or app.debug:
        return
    app.sentry = Sentry(
        app,
        dsn=app.config['SENTRY_DSN'],
        register_signal=True,
        wrap_wsgi=True,
        logging=True,
        level=app.config['SENTRY_ERROR_LEVEL']
    )


def get_app(config=None):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    if config is None:
        config = {}

    abs_path = os.path.abspath(os.path.dirname(__file__))
    config.setdefault('APP_ABSPATH', abs_path)

    for key in dir(eden.factory.settings):
        if key.isupper():
            config.setdefault(key, getattr(eden.factory.settings, key))

    config.setdefault('DOMAIN', {})

    app = eve.Eve(
        settings=config,
        json_encoder=MongoJSONEncoder,
        validator=EdenValidator
    )
    configure_logging(app)
    eden.app = app

    custom_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([abs_path + '/../templates'])
    ])
    app.jinja_loader = custom_loader

    @app.errorhandler(EdenError)
    def client_error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`eden.EdenError` class
        """
        return send_response(
            None, (error.to_dict(), None, None, error.status_code))

    @app.errorhandler(500)
    def server_error_handler(error):
        """Log server errors."""
#         app.sentry.captureException()
#         app.logger.exception(error)
        return_error = EdenApiError.internalError()
        return client_error_handler(return_error)

    init_celery(app)

    for module_name in app.config['INSTALLED_APPS']:
        app_module = importlib.import_module(module_name)
        try:
            app_module.init_app(app)
        except AttributeError:
            app.logger.error('App %s not initialized' % (module_name))

    for resource in eden.DOMAIN:
        app.register_resource(resource, eden.DOMAIN[resource])

    for blueprint in eden.BLUEPRINTS:
        prefix = app.api_prefix or None
        app.register_blueprint(blueprint, url_prefix=prefix)

    for name, jinja_filter in eden.JINJA_FILTERS.items():
        app.jinja_env.filters[name] = jinja_filter

#     app.sentry = sentry
#     sentry.init_app(app)

    return app
