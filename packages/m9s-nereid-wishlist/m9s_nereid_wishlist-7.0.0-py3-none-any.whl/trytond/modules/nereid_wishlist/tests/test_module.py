# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from unittest.mock import patch

from trytond.config import config
from trytond.modules.nereid_cart_b2c.tests import (
    create_countries, create_product_template, create_website)
from trytond.modules.payment_gateway.tests import create_payment_gateway
from trytond.pool import Pool
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

from nereid import current_user
from nereid.testing import NereidModuleTestCase

config.set('database', 'path', '/tmp')


class NereidWishlistTestCase(NereidModuleTestCase):
    'Test Nereid Wishlist module'
    module = 'nereid_wishlist'
    extras = ['payment_gateway']

    def setUp(self):
        self.templates = {
            'wishlists.jinja':
                '{{ current_user.wishlists | length }}',
            'wishlist.jinja':
                '{{ wishlist.name }}',
            }

        # Patch SMTP Lib
        self.smtplib_patcher = patch('smtplib.SMTP')
        self.PatchedSMTP = self.smtplib_patcher.start()

    def tearDown(self):
        # Unpatch SMTP Lib
        self.smtplib_patcher.stop()

    @with_transaction()
    def test_0010_create_wishlist(self):
        """
        Test to add a new wishlist.
        If the wishlist already exists just return that wishlist
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')
        Address = pool.get('party.address')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:

            # Guest user tries to create wishlist
            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)

            response = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)

            self.assertEqual(len(current_user.wishlists), 1)
            self.assertEqual(rv.status_code, 302)

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(current_user.wishlists[0].name, 'Test')

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    }, headers=[('X-Requested-With', 'XMLHttpRequest')])
            self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0020_view_list_of_wishlists(self):
        """
        Test to view all wishlists
        """
        pool = Pool()
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        app = self.get_app()
        with app.test_client() as c:
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test1',
                    })
            self.assertEqual(rv.status_code, 302)

            rv = c.get('/en/wishlists')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), '2')

    @with_transaction()
    def test_0030_remove_wishlist(self):
        """
        Test to remove a wishlist
        """
        pool = Pool()
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        app = self.get_app()
        with app.test_client() as c:
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test1',
                    })
            self.assertEqual(rv.status_code, 302)

            self.assertEqual(
                len(current_user.wishlists), 2)

            rv = c.delete(
                '/en/wishlists/%d' % (current_user.wishlists[0].id,))
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(len(current_user.wishlists), 1)

            rv = c.delete(
                '/en/wishlists/%d' % (current_user.wishlists[0].id,),
                headers=[('X-Requested-With', 'XMLHttpRequest')])
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(len(current_user.wishlists), 0)

    @with_transaction()
    def test_0040_wishlist_products(self):
        """
        Test to add/remove a product to wishlist.
        """
        pool = Pool()
        Country = pool.get('country.country')
        Company = pool.get('company.company')
        NereidUser = pool.get('nereid.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        company, = Company.search([])

        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        template2, = create_product_template(
            'product-2',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('20'),
            }],
            uri='product-2',
        )
        product1 = template1.products[0]
        product2 = template2.products[0]

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # Add a product without creating any wishlist
            rv = c.post('/en/wishlists/products',
                data={
                    'product': product1.id,
                    'action': 'add',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(len(current_user.wishlists), 1)
            self.assertEqual(len(current_user.wishlists[0].products), 1)

            # Add a product to a specific wishlist
            rv = c.post('/en/wishlists/products',
                data={
                    'product': product2.id,
                    'action': 'add',
                    'wishlist': current_user.wishlists[0].id,
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(len(current_user.wishlists[0].products), 2)

            # Remove the first product
            rv = c.post('/en/wishlists/products',
                data={
                    'product': product1.id,
                    'wishlist': current_user.wishlists[0].id,
                    'action': 'remove',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(len(current_user.wishlists[0].products), 1)

            # Try to remove a non-existent product
            rv = c.post('/en/wishlists/products',
                data={
                    'product': 11,
                    'wishlist': current_user.wishlists[0].id,
                    'action': 'remove',
                    })
            self.assertEqual(rv.status_code, 404)

            # XXX Testing bug?
            # current_user gets lost in subsequent tests, therefore we
            # instanciate for now the current_user as NereidUser to be used for
            # reference starting from line 331
            user, = NereidUser.browse([current_user.id])
            # Try to use a non-existent action
            rv = c.post('/en/wishlists/products',
                data={
                    'product': 11,
                    'wishlist': current_user.wishlists[0].id,
                    'action': 'other',
                    })
            self.assertEqual(rv.status_code, 404)

            # Test to see if a non-exsitent wishlist is found
            with self.assertRaises(ValueError):
                c.post('/en/wishlists/products',
                    data={
                        'product': product1.id,
                        'wishlist': 10,
                        'action': 'add',
                        })
            # xhr request
            rv = c.post('/en/wishlists/products',
                data={
                    'product': product2.id,
                    'action': 'remove',
                    'wishlist': user.wishlists[0].id,
                    }, headers=[('X-Requested-With', 'XMLHttpRequest')])
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(len(user.wishlists[0].products), 0)

            rv = c.post('/en/wishlists/products',
                data={
                    'product': product2.id,
                    'action': 'add',
                    'wishlist': user.wishlists[0].id,
                    }, headers=[('X-Requested-With', 'XMLHttpRequest')])
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(len(user.wishlists[0].products), 1)

    @with_transaction()
    def test_0050_render_single_wishlist(self):
        """
        Test to render a single wishlist.
        """
        pool = Pool()
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        app = self.get_app()
        with app.test_client() as c:
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(len(current_user.wishlists), 1)

            rv = c.get('/en/wishlists/%d' % (
                    current_user.wishlists[0].id,))
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Test')

            # Xhr request
            rv = c.get('/en/wishlists/%d'
                % (current_user.wishlists[0].id, ),
                headers=[('X-Requested-With', 'XMLHttpRequest')])

            self.assertEqual(rv.status_code, 200)

            user1_wishlist_id = current_user.wishlists[0].id

            # User trying to access wishlist of another user
            response = c.post('/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.get('/en/wishlists/%d' % (user1_wishlist_id, ))
            self.assertEqual(rv.status_code, 404)

    @with_transaction()
    def test_0060_rename_wishlist(self):
        """
        Test rename a wishlist
        """
        pool = Pool()
        Country = pool.get('country.country')
        Wishlist = pool.get('wishlist.wishlist')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        app = self.get_app()
        with app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.post('/en/wishlists',
                data={
                    'name': 'Test',
                    })
            self.assertEqual(rv.status_code, 302)

            rv = c.post(
                '/en/wishlists',
                data={
                    'name': 'existing',
                    })

            wishlist = current_user.wishlists[0]

            self.assertEqual(rv.status_code, 302)
            self.assertEqual(wishlist.name, 'Test')

            rv = c.post('/en/wishlists/%d' % (wishlist.id, ),
                data={
                    'name': 'existing',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(wishlist.name, 'Test')

            rv = c.post('/en/wishlists/%d' % (wishlist.id, ),
                data={
                    'name': 'Test2',
                    })

            self.assertEqual(rv.status_code, 302)
            wishlist = Wishlist(wishlist.id)    # reload the record
            self.assertEqual(wishlist.name, 'Test2')

    @with_transaction()
    def test_0070_copy_product(self):
        """
        Duplicating a product should not copy wishlists
        """
        pool = Pool()
        Country = pool.get('country.country')
        Wishlist = pool.get('wishlist.wishlist')
        NereidUser = pool.get('nereid.user')
        Product = pool.get('product.product')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        template2, = create_product_template(
            'product-2',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('20'),
            }],
            uri='product-2',
        )
        product1 = template1.products[0]
        product2 = template2.products[0]

        registered_user, = NereidUser.search([
                'email', '=', 'info@m9s.biz',
                ])
        wishlist = Wishlist()
        wishlist.nereid_user = registered_user
        wishlist.name = 'Books I Want to Read!'
                    #'products': [('add', [product1.id])]
        wishlist.products = [product1]
        wishlist.save()

        self.assertEqual(len(product1.wishlists), 1)

        product2, = Product.copy([product1])

        self.assertEqual(len(product2.wishlists), 0)

    @with_transaction()
    def test_0080_access_public_private_wishlist(self):
        """
        Test to check working of public and private wishlist.
        """
        pool = Pool()
        Country = pool.get('country.country')
        Wishlist = pool.get('wishlist.wishlist')
        NereidUser = pool.get('nereid.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        registered_user, = NereidUser.search([
                'email', '=', 'info@m9s.biz',
                ])
        registered_user2, = NereidUser.search([
                'email', '=', 'mail@m9s.biz',
                ])

        user_private_wishlist, = Wishlist.create([{
            'nereid_user': registered_user,
            'name': 'Books I Want to Read!',
        }])
        user2_private_wishlist, = Wishlist.create([{
            'nereid_user': registered_user2,
            'name': 'Books I do not Want to Read!',
        }])
        user2_public_wishlist, = Wishlist.create([{
            'nereid_user': registered_user2,
            'name': 'Books I do not like!',
            'is_public': True
        }])

        app = self.get_app()
        with app.test_client() as c:
            # Guest user trying to access a private wishlist
            rv = c.get(
                '/en/wishlists/%d' % (user_private_wishlist,))
            self.assertEqual(rv.status_code, 404)

            # Guest user trying to access a public wishlist
            rv = c.get(
                '/en/wishlists/%d' % (user2_public_wishlist,))
            self.assertEqual(rv.status_code, 200)

            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # User trying to access its own wishlist
            rv = c.get(
                '/en/wishlists/%d' % (user_private_wishlist,))
            self.assertEqual(rv.status_code, 200)

            # User trying to access private wishlist of another user
            rv = c.get(
                '/en/wishlists/%d' % (user2_private_wishlist,))
            self.assertEqual(rv.status_code, 404)

            # User trying to access public wishlist of another user
            rv = c.get(
                '/en/wishlists/%d' % (user2_public_wishlist,))
            self.assertEqual(rv.status_code, 200)


del NereidModuleTestCase
