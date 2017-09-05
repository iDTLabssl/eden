# -*- coding: utf-8; -*-
#
# This file is part of Eden.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/eden/license

from eden.tests import TestCase


# TODO test validators
class EdenValidatorTest(TestCase):
    """Base class for the EdenValidator class tests."""

    def setUp(self):
        super(EdenValidatorTest, self).setUp()
        klass = self._get_target_class()
        self.validator = klass(schema={})
        self.validator.document = {}
        self._errors = {}

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from eden.validator import EdenValidator
        except ImportError:
            self.fail("Could not import class under test (EdenValidator)")
        else:
            return EdenValidator
