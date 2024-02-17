# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import warnings

import jinja2

from trytond.pool import PoolMeta
from trytond.tests.test_tryton import with_transaction

from nereid import template_filter, url_for
from nereid.helpers import slugify
from nereid.testing import POOL as Pool

from test_templates import BaseTestCase


class TestURLfor(BaseTestCase):
    """
    Test the functionality of the url_for helper
    """

    @with_transaction()
    def test_0010_simple(self):
        """
        Generate a simple URL
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_request_context('/'):
            self.assertEqual(url_for('nereid.website.home'), '/')

    @with_transaction()
    def test_0020_external(self):
        """
        Create an external URL
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_request_context('/'):
            self.assertEqual(url_for('nereid.website.home', _external=True),
                'http://localhost/')

    @with_transaction()
    def test_0030_schema(self):
        """
        Change the schema to https
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_request_context('/'):
            self.assertEqual(url_for('nereid.website.home', _external=True,
                    _scheme='https'), 'https://localhost/')


class NereidWebsite(metaclass=PoolMeta):
    __name__ = 'nereid.website'

    @classmethod
    @template_filter()
    def reverse_test(cls, s):
        return s[::-1]


class TestHelperFunctions(BaseTestCase):
    '''
    Test case to test various helper functions introduced by nereid
    '''

    @classmethod
    def setUpClass(cls):
        Pool.register(NereidWebsite, module='nereid_base', type_='model')
        Pool.init(update=['nereid_base'])

    @classmethod
    def tearDownClass(cls):
        mpool = Pool.classes['model'].setdefault('nereid_base', [])
        del(mpool[NereidWebsite])
        Pool.init(update=['nereid_base'])

    @with_transaction()
    def test_template_filter(self):
        '''
        Test the template filter decorator implementation
        '''
        self.setup_defaults()
        templates = {
            'home.jinja': "{{ 'abc'|reverse_test }}"
            }
        app = self.get_app()
        # loaders is usually lazy loaded
        # Pre-fetch it so that the instance attribute _loaders will exist
        app.jinja_loader.loaders
        app.jinja_loader._loaders.insert(0, jinja2.DictLoader(templates))

        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.data, b'cba')

    def test_slugify(self):
        "Test slugify"
        self.assertEqual(slugify('unicode ♥ is ☢'), 'unicode-is')

    def test_slugify_hyphenate(self):
        "Test hyphenate in slugify"
        self.assertEqual(slugify('foo bar', hyphenate='_'), 'foo_bar')

    def test_slugify_lower(self):
        "Test lower case in slugify"
        self.assertEqual(slugify('Foo BaR'), 'foo-bar')



def suite():
    "Nereid Helpers test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestURLfor),
        unittest.TestLoader().loadTestsFromTestCase(TestHelperFunctions),
    ])
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
