# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/eden/license

import re

from bson import ObjectId
from eve.io.mongo import Validator
from eve.utils import config
from werkzeug.datastructures import FileStorage


ERROR_PATTERN = {'pattern': 1}
ERROR_UNIQUE = {'unique': 1}
ERROR_MINLENGTH = {'minlength': 1}
ERROR_REQUIRED = {'required': 1}
ERROR_JSON_LIST = {'json_list': 1}


class EdenValidator(Validator):

    def _validate_mapping(self, mapping, field, value):
        pass

    def _validate_index(self, field, value):
        pass

    def _validate_type_phone_number(self, field, value):
        """ Enables validation for `phone_number` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        if not re.match("^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$", value):
            self._error(field, ERROR_PATTERN)

    def _validate_type_email(self, field, value):
        """ Enables validation for `email` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        regex = "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@" \
                "(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+(?:\.[a-z0-9](?:[a-z0-9-]{0,4}[a-z0-9])?)*$"
        if not re.match(regex, value, re.IGNORECASE):
            self._error(field, ERROR_PATTERN)

    def _validate_type_file(self, field, value):
        """Enables validation for `file` schema attribute."""
        if not isinstance(value, FileStorage):
            self._error(field, ERROR_PATTERN)

    def _set_id_query(self, query):
            if self._id:
                try:
                    query[config.ID_FIELD] = {'$ne': ObjectId(self._id)}
                except:
                    query[config.ID_FIELD] = {'$ne': self._id}

    def _validate_type_json_list(self, field, value):
        """It will fail later when loading."""
        if not isinstance(value, type('')):
            self._error(field, ERROR_JSON_LIST)
