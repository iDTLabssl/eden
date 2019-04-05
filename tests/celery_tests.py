# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/eden/license

from datetime import datetime

from bson import ObjectId
from eve.utils import date_to_str

from eden.celery_app import try_cast, loads
from eden.tests import TestCase


class CeleryTestCase(TestCase):
    _id = ObjectId('528de7b03b80a13eefc5e610')

    def test_cast_objectid(self):
        self.assertEqual(try_cast(str(self._id)), self._id)

    def test_cast_datetime(self):
        date = datetime(2012, 12, 12, 12, 12, 12, 0)
        with self.app.app_context():
            s = date_to_str(date)
            self.assertEqual(try_cast(s).day, date.day)

    def test_loads_args(self):
        return
        s = b'{"args": [{"_id": "528de7b03b80a13eefc5e610", "_updated": "Fri, 03 Oct 2014 08:16:52 GMT"}]}'
        o = loads(s)
        self.assertEqual(o['args'][0]['_id'], self._id)
        self.assertIsInstance(o['args'][0]['_updated'], datetime)

    def test_loads_kwargs(self):
        s = b'''{"kwargs": "{}", "pid": 24998, "eta": null}'''
        o = loads(s)
        self.assertEqual({}, o['kwargs'])
        self.assertIsNone(o['eta'])
