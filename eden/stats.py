# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/eden/license

"""Superdesk statistics.

Using statsd client to push metrics via udp to statsd which can send it further.
"""
from eve_statsd import StatsD


def init_app(app):
    StatsD(app)
