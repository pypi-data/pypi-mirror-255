# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
import pickle
import unittest

from email.header import decode_header

import pycountry

from secure_cookie.session import FilesystemSessionStore

import trytond.tests.test_tryton

from trytond.cache import Cache
from trytond.tests.test_tryton import CONTEXT, DB_NAME, with_transaction
from trytond.transaction import Transaction

from nereid import LazyRenderer, render_email, render_template
from nereid.contrib.locale import Babel
from nereid.sessions import Session
from nereid.testing import POOL as pool
from nereid.testing import NereidTestApp, NereidTestCase


class BaseTestCase(NereidTestCase):

    def setUp(self):
        trytond.tests.test_tryton.activate_module('nereid_test')

        self.nereid_website_obj = pool.get('nereid.website')
        self.nereid_website_locale_obj = pool.get('nereid.website.locale')
        self.nereid_user_obj = pool.get('nereid.user')
        self.company_obj = pool.get('company.company')
        self.currency_obj = pool.get('currency.currency')
        self.language_obj = pool.get('ir.lang')
        self.country_obj = pool.get('country.country')
        self.subdivision_obj = pool.get('country.subdivision')
        self.party_obj = pool.get('party.party')

    def create_countries(self, count=5):
        """
        Create some sample countries and subdivisions
        """
        for country in list(pycountry.countries)[0:count]:
            country_id, = self.country_obj.create([{
                'name': country.name,
                'code': country.alpha_2,
                }])
            try:
                divisions = pycountry.subdivisions.get(
                    country_code=country.alpha_2)
            except KeyError:
                pass
            else:
                self.subdivision_obj.create([{
                    'country': country_id,
                    'name': subdivision.name,
                    'code': subdivision.code,
                    'type': subdivision.type.lower(),
                    } for subdivision in list(divisions)[0:count]])

    def setup_defaults(self):
        """
        Setup the defaults
        """
        # Q&D hack to avoid repeated setup
        # TODO: make a clean setup
        if self.currency_obj.search([('code', '=', 'USD')]):
            return

        usd, = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            }])
        self.party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        self.company, = self.company_obj.create([{
            'party': self.party,
            'currency': usd,
            }])
        self.create_countries()
        self.available_countries = self.country_obj.search([], limit=5)

        en, = self.language_obj.search([('code', '=', 'en')])
        currency, = self.currency_obj.search([('code', '=', 'USD')])
        locale, = self.nereid_website_locale_obj.create([{
            'code': 'en',
            'language': en,
            'currency': currency,
            }])
        self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': 1,
            'default_locale': locale,
            'countries': [('add', self.available_countries)],
            }])

    def get_app(self, **options):
        app = NereidTestApp(template_folder=os.path.abspath(
                os.path.join(os.path.dirname(__file__), 'templates')))
        if 'SECRET_KEY' not in options:
            options['SECRET_KEY'] = 'secret-key'
        app.config['TEMPLATE_PREFIX_WEBSITE_NAME'] = False
        app.config.update(options)
        app.config['DATABASE_NAME'] = DB_NAME
        app.config['DEBUG'] = True
        app.session_interface.session_store = FilesystemSessionStore(
            '/tmp', session_class=Session)

        # Initialise the app now
        app.initialise()

        # Load babel as it is a required extension anyway
        Babel(app)
        return app


class TestTemplateLoading(BaseTestCase):
    '''
    Test the loading of templates
    '''
    @with_transaction()
    def test_0005_loaders(self):
        '''
        Confirm the paths in the loaders
        '''
        self.setup_defaults()
        app = self.get_app()

        # There must be two loaders, one from the searchpath
        # relative to this folder and the other from
        # nereid package
        self.assertEqual(len(app.jinja_loader.loaders), 2)

    @with_transaction()
    def test_0010_local_loading(self):
        '''
        Render template from local searchpath
        '''
        self.setup_defaults()
        app = self.get_app()

        with app.test_request_context('/'):
            self.assertEqual(render_template('from-local.html'),
                'from-local-folder')

    @with_transaction()
    def test_0020_module_loading(self):
        '''
        Render template from module templates searchpath
        '''
        self.setup_defaults()
        app = self.get_app()

        # The result may differ according to modules installed, the template is
        # in nereid_test as well as in nereid_base
        with app.test_request_context('/'):
            self.assertEqual(render_template('tests/from-module.html'),
                'from-nereid-test-module')

    @with_transaction()
    def test_0030_local_overwrites_module(self):
        '''
        Look for a template which has a local presence and also
        in the package, but the one rendered is from the local folder
        '''
        self.setup_defaults()
        app = self.get_app()

        with app.test_request_context('/'):
            self.assertEqual(render_template('tests/exists-both.html'),
                'content-from-local')

    def test_0040_inheritance(self):
        '''Test if templates are read in the reverse order of the tryton
        module dependency graph. To test this we install the test
        module now and then try to load a template which is different
        with the test module.
        '''
        trytond.tests.test_tryton.activate_module('nereid_base')

        with Transaction().start(DB_NAME, 1, CONTEXT) as txn:  # noqa
            # Add nereid_test also to list of modules installed so
            # that it is also added to the templates path
            app = self.get_app()

            self.assertEqual(len(app.jinja_loader.loaders), 2)

            with app.test_request_context('/'):
                self.assertEqual(render_template('tests/from-module.html'),
                    'from-nereid-test-module')

            txn.rollback()
            Cache.drop(DB_NAME)

    @with_transaction()
    def test_0050_prefix_loader(self):
        """
        Test the SiteNamePrefixLoader
        """
        self.setup_defaults()
        app = self.get_app(TEMPLATE_PREFIX_WEBSITE_NAME=True)

        with app.test_request_context('/'):
            self.assertEqual(render_template('site-specific-template.html'),
                'content-from-localhost-site-specific-template')

    @with_transaction()
    def test_0060_render_email(self):
        '''
        Render Email with template from local searchpath
        '''
        self.setup_defaults()
        app = self.get_app()

        sender = 'Sender <sender@m9s.biz>'

        with app.test_request_context('/'):
            email_message = render_email(sender, 'receiver@m9s.biz',
                'Dummy subject of email', text_template='from-local.html',
                cc='cc@m9s.biz')
            self.assertEqual(
                decode_header(email_message['From'])[0],
                (sender, None))
            self.assertEqual(
                decode_header(email_message['Subject'])[0],
                ('Dummy subject of email'.encode('utf-8'), 'utf-8'))

    @with_transaction()
    def test_0070_render_email_unicode(self):
        '''
        Render email with unicode chars in Subject, From and To.
        '''
        self.setup_defaults()
        app = self.get_app()

        sender = 'Björn Bär <sender@m9s.biz>'

        with app.test_request_context('/'):
            email_message = render_email(
                sender, 'receiver@m9s.biz', 'Dummy sübject øf email',
                text_template='from-local.html', cc='cc@m9s.biz')
            self.assertEqual(decode_header(email_message['From'])[0],
                (sender, None))
            self.assertEqual(decode_header(email_message['Subject'])[0],
                ('Dummy sübject øf email'.encode('utf-8'), 'utf-8'))
            self.assertEqual(decode_header(email_message['To'])[0],
                ('receiver@m9s.biz', None))

    @with_transaction()
    def test_0080_render_email_text_only(self):
        '''
        Render email text part alone
        '''
        self.setup_defaults()
        app = self.get_app()

        sender = 'Sender <sender@m9s.biz>'

        with app.test_request_context('/'):
            email_message = render_email(sender, 'receiver@m9s.biz',
                'Dummy subject of email', text_template='from-local.html')
            self.assertEqual(decode_header(email_message['Subject'])[0],
                ('Dummy subject of email'.encode('utf-8'), 'utf-8'))

            # Message type should be text/plain
            self.assertFalse(email_message.is_multipart())
            self.assertEqual(email_message.get_content_type(), 'text/plain')

    @with_transaction()
    def test_0090_render_email_html_only(self):
        '''
        Render email html part alone
        '''
        self.setup_defaults()
        app = self.get_app()

        sender = 'Sender <sender@m9s.biz>'

        with app.test_request_context('/'):
            email_message = render_email(sender, 'receiver@m9s.biz',
                'Dummy subject of email', html_template='from-local.html')
            self.assertEqual(decode_header(email_message['Subject'])[0],
                ('Dummy subject of email'.encode('utf-8'), 'utf-8'))

            # Message type should be text/html
            self.assertFalse(email_message.is_multipart())
            self.assertEqual(email_message.get_content_type(), 'text/html')

    @with_transaction()
    def test_0100_render_email_text_n_html_only(self):
        '''
        Render email text and html parts, but no attachments
        '''
        self.setup_defaults()
        app = self.get_app()

        sender = 'Sender <sender@m9s.biz>'

        with app.test_request_context('/'):
            email_message = render_email(sender, 'receiver@m9s.biz',
                'Dummy subject of email', text_template='from-local.html',
                html_template='from-local.html')
            self.assertEqual(decode_header(email_message['Subject'])[0],
                ('Dummy subject of email'.encode('utf-8'), 'utf-8'))

            # Message type should be multipart/alternative
            self.assertTrue(email_message.is_multipart())
            self.assertEqual(email_message.get_content_type(),
                'multipart/alternative')

            # Ensure that there are two subparts
            self.assertEqual(len(email_message.get_payload()), 2)

            # Ensure that the subparts are 1 text and html part
            payload_types = set([
                    p.get_content_type() for p in email_message.get_payload()])
            self.assertEqual(set(['text/plain', 'text/html']), payload_types)

    @with_transaction()
    def test_0110_email_with_attachments(self):
        '''
        Send an email with text, html and an attachment
        '''
        self.setup_defaults()
        app = self.get_app()

        sender = 'Sender <sender@m9s.biz>'

        with app.test_request_context('/'):
            email_message = render_email(sender, 'receiver@m9s.biz',
                'Dummy subject of email', text_template='from-local.html',
                html_template='from-local.html',
                attachments={'filename.pdf': 'my glorious PDF content'})

            self.assertEqual(decode_header(email_message['Subject'])[0],
                ('Dummy subject of email'.encode('utf-8'), 'utf-8'))

            # Message type should be multipart/mixed
            self.assertTrue(email_message.is_multipart())
            self.assertEqual(email_message.get_content_type(),
                'multipart/mixed')

            # Ensure that there are two subparts
            self.assertEqual(len(email_message.get_payload()), 2)

            # Ensure that the subparts are alternative and octet-stream parts
            payload_types = set([
                p.get_content_type() for p in email_message.get_payload()])
            self.assertEqual(
                set(['multipart/alternative', 'application/octet-stream']),
                payload_types)

            # Drill into the alternative part and ensure that there is
            # both the text part and html part in it.
            for part in email_message.get_payload():
                if part.get_content_type() == 'multipart/alternative':
                    # Ensure that there are two subparts
                    # 1. text/plain
                    # 2. text/html
                    self.assertEqual(len(email_message.get_payload()), 2)
                    payload_types = set([
                        p.get_content_type() for p in part.get_payload()])
                    self.assertEqual(set(['text/plain', 'text/html']),
                        payload_types)
                    break
            else:
                self.fail('Alternative part not found')


class TestLazyRendering(BaseTestCase):
    '''
    Test the lazy rendering of templates
    '''

    @with_transaction()
    def test_0010_change_context(self):
        '''
        Render template from local searchpath
        '''
        self.setup_defaults()
        app = self.get_app()

        with app.test_request_context('/'):
            self.assertEqual(render_template(
                    'tests/test-changing-context.html',
                    variable="a"), 'a')
            lazy_template = render_template(
                'tests/test-changing-context.html',
                variable="a")
            self.assertTrue(isinstance(lazy_template, LazyRenderer))

            # Now change the value of the variable in the context and
            # see if the template renders with the new value
            lazy_template.context['variable'] = "b"
            self.assertEqual(lazy_template, "b")

            # Make a unicode of the same template
            unicode_of_response = str(lazy_template)
            self.assertEqual(unicode_of_response, "b")
            self.assertTrue(isinstance(unicode_of_response, str))

    def test_0020_pickling(self):
        '''
        Test if the lazy rendering object can be pickled and rendered
        with a totally different context (when no application, request
        or transaction bound objects are present).
        '''
        with Transaction().start(DB_NAME, 1, CONTEXT) as txn:
            self.setup_defaults()
            app = self.get_app()

            with app.test_request_context('/'):
                response = render_template(
                    'tests/test-changing-context.html',
                    variable="a")
                self.assertEqual(response, 'a')
                pickled_response = pickle.dumps(response)

            txn.rollback()
            # Drop the cache as the transaction is rollbacked
            Cache.drop(DB_NAME)

        with Transaction().start(DB_NAME, 1, CONTEXT) as txn:
            self.setup_defaults()
            app = self.get_app()

            with app.test_request_context('/'):
                response = pickle.loads(pickled_response)
                self.assertEqual(response, 'a')

            txn.rollback()
            # Drop the cache as the transaction is rollbacked
            Cache.drop(DB_NAME)

    @with_transaction()
    def test_0030_simple_render(self):
        '''
        Simply render a template.
        '''
        self.setup_defaults()
        app = self.get_app()
        app.testing = True

        with app.test_client() as c:
            response = c.get('/registration')
            self.assertEqual(response.status_code, 200)

    def test_0040_headers(self):
        '''
        Change registrations headers and check

        Note: Whenever the URL adapter is changed by activation of a module,
        method 'get_url_adapter' (website) must not be cached by memoize,
        otherwise the new routes of the module won't be registered (i.e. the
        old cache used).
        '''
        trytond.tests.test_tryton.activate_module('nereid_test')
        with Transaction().start(DB_NAME, 1, CONTEXT) as txn:
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                response = c.get('/test-lazy-renderer')
                self.assertEqual(response.headers['X-Test-Header'], 'TestValue')
                self.assertEqual(response.status_code, 201)

            txn.rollback()
            # Drop the cache as the transaction is rollbacked
            Cache.drop(DB_NAME)


def suite():
    "Nereid Template Loading test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestTemplateLoading),
        unittest.TestLoader().loadTestsFromTestCase(TestLazyRendering),
    ])
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
