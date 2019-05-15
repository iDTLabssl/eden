# # -*- coding: utf-8; -*-
# #
# # This file is part of Superdesk.
# #
# # Copyright 2013, 2014 Sourcefabric z.u. and contributors.
# #
# # For the full copyright and license information, please see the
# # AUTHORS and LICENSE files distributed with this source code, or
# # at https://www.sourcefabric.org/eden/license
#
# """
# Created on May 29, 2014
#
# @author: ioan
# """
#
# import logging
# from datetime import datetime
#
# import werkzeug
# from bson import ObjectId
# from celery import Celery
# from eve.io.mongo import MongoJSONEncoder
# from flask import json, current_app as app
# from kombu.serialization import register
#
# import eden
# from eden.errors import EdenError
#
# logger = logging.getLogger(__name__)
# celery = Celery(__name__)
# TaskBase = celery.Task
#
#
# def try_cast(v):
#     try:
#         return datetime.strptime(v, app.config['DATE_FORMAT'])
#     except:
#         try:
#             try:
#                 r = ObjectId(unicode(v))
#             except NameError:
#                 # We're on Python 3 so it's all unicode # already.
#                 r = ObjectId(v)
#             return r
#         except:
#             return v
#         else:
#             return v
#
#
# def cast_item(o):
#     with eden.app.app_context():
#         for k, v in o.items():
#             if isinstance(v, dict):
#                 cast_item(v)
#             elif isinstance(v, bool):
#                 pass
#             else:
#                 o[k] = try_cast(v)
#
#
# def loads(s):
#     o = json.loads(s)
#
#     if not o.get('args', None):
#         o['args'] = []
#
#     if not o.get('kwargs', None):
#         o['kwargs'] = {}
#
#     for v in o['args']:
#         if isinstance(v, dict):
#             cast_item(v)
#
#     kwargs = o['kwargs']
#     if isinstance(kwargs, (str, unicode)):
#         o['kwargs'] = json.loads(kwargs)
#         kwargs = o['kwargs']
#     for k, v in kwargs.items():
#         if isinstance(v, str):
#             kwargs[k] = try_cast(v)
#
#         if isinstance(v, list):
#             kwargs[k] = [try_cast(val) for val in v]
#
#         if isinstance(v, dict):
#             cast_item(v)
#
#     return o
#
#
# def dumps(o):
#     with eden.app.app_context():
#         return MongoJSONEncoder().encode(o)
#
#
# register('eve/json', dumps, loads, content_type='application/json')
#
#
# def handle_exception(exc):
#     """Log exception to logger and sentry."""
#     logger.exception(exc)
#     eden.app.sentry.captureException(exc)
#
#
# class AppContextTask(TaskBase):
#     abstract = True
#     serializer = 'eve/json'
#     app_errors = (
#         EdenError,
#         werkzeug.exceptions.InternalServerError,  # mongo layer err
#     )
#
#     def __call__(self, *args, **kwargs):
#         with eden.app.app_context():
#             try:
#                 return super(AppContextTask, self).__call__(*args, **kwargs)
#             except self.app_errors as e:
#                 handle_exception(e)
#
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         with eden.app.app_context():
#             handle_exception(exc)
#
#
# celery.Task = AppContextTask
#
#
# def init_celery(app):
#     celery.conf.update(app.config)
#     app.celery = celery
#
#
# def update_key(key, flag=False, db=None):
#     if flag:
#         crt_value = db.incr(key)
#     else:
#         crt_value = db.get(key)
#
#     if crt_value:
#         crt_value = int(crt_value)
#     else:
#         crt_value = 0
#     return crt_value
