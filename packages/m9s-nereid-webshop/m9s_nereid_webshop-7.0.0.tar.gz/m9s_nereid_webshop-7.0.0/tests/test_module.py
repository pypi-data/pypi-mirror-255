# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import json

from datetime import date
from decimal import Decimal
from os.path import join
from unittest.mock import patch

from cssutils import CSSParser

from trytond.config import config
from trytond.modules.company.tests import CompanyTestMixin
from trytond.modules.gift_card.tests.test_module import create_product
from trytond.modules.nereid_cart_b2c.tests import (
    create_countries, create_product_template, create_website)
from trytond.modules.payment_gateway.tests import create_payment_gateway
from trytond.pool import Pool
from trytond.tests.test_tryton import USER
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

from nereid import request
from nereid.testing import NereidModuleTestCase

config.set('email', 'from', 'from@xyz.com')
css_dir = 'static/css/'


def create_test_products():
    pool = Pool()
    Category = pool.get('product.category')

    category2, = Category.create([
        {
            'name': 'Category 2',
        }])
    category3, = Category.create([
        {
            'name': 'Category 3',
        }])

    template1, = create_product_template(
        'Product 1',
        [{
            'type': 'goods',
            'salable': True,
            'list_price': Decimal('10'),
        }],
        uri='product-1',
    )
    template2, = create_product_template(
        'Product 2',
        [{
            'type': 'goods',
            'salable': True,
            'list_price': Decimal('10'),
        }],
        uri='product-2',
    )
    template3, = create_product_template(
        'Product 3',
        [{
            'type': 'goods',
            'salable': True,
            'list_price': Decimal('10'),
        }],
        uri='product-3',
    )
    template4, = create_product_template(
        'Product 4',
        [{
            'type': 'goods',
            'salable': True,
            'list_price': Decimal('10'),
        }],
        uri='product-4',
    )
    product2 = template2.products[0]
    product3 = template3.products[0]
    product4 = template4.products[0]

    product2.categories = [category2]
    product2.save()
    product3.categories = [category3]
    product3.save()
    product4.categories = [category3]
    product4.displayed_on_eshop = False
    product4.save()


def validate_css(filename):
    """
    Uses cssutils to validate a css file.
    Prints output using a logger.
    """
    CSSParser(raiseExceptions=True).parseFile(filename, validate=True)


class NereidWebshopTestCase(CompanyTestMixin, NereidModuleTestCase):
    'Test Nereid Webshop module'
    module = 'nereid_webshop'
    extras = ['nereid_catalog_variants', 'sale_shipment_cost']

    def setUp(self):
        self.templates = {
            'shopping-cart.jinja':
                'Cart:{{ cart.id }},{{get_cart_size()|round|int}},'
                '{{cart.sale.total_amount}}',
            'product.jinja':
                '{{ product.name }}',
            'catalog/gift-card.html':
                '{{ product.id }}',

            }

        # Patch SMTP Lib
        self.smtplib_patcher = patch('smtplib.SMTP')
        self.PatchedSMTP = self.smtplib_patcher.start()

    def tearDown(self):
        # Unpatch SMTP Lib
        self.smtplib_patcher.stop()

    @with_transaction()
    def test_0010_website_sitemap(self):
        """
        Tests the rendering of the sitemap.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Node = pool.get('product.tree_node')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        node1, = Node.create([{
            'name': 'Node1',
            'type_': 'catalog',
            'slug': 'node1',
        }])

        node2, = Node.create([{
            'name': 'Node2',
            'type_': 'catalog',
            'slug': 'node2',
            'display': 'product.template',
        }])

        node3, = Node.create([{
            'name': 'Node3',
            'type_': 'catalog',
            'slug': 'node3',
        }])

        node4, = Node.create([{
            'name': 'Node4',
            'type_': 'catalog',
            'slug': 'node4',
        }])

        node5, = Node.create([{
            'name': 'Node5',
            'type_': 'catalog',
            'slug': 'node5',
        }])

        Node.write([node2], {
            'parent': node1
        })

        Node.write([node3], {
            'parent': node1,
        })

        Node.write([node4], {
            'parent': node3,
        })

        Node.write([node5], {
            'parent': node4,
        })

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/sitemap')
            self.assertEqual(rv.status_code, 200)

            self.assertIn('Node1', rv.data.decode('utf-8'))
            self.assertIn('Node2', rv.data.decode('utf-8'))
            self.assertIn('Node3', rv.data.decode('utf-8'))
            self.assertIn('Node4', rv.data.decode('utf-8'))

            # Beyond depth of 2, will not show.
            self.assertNotIn('Node5', rv.data.decode('utf-8'))

    @with_transaction()
    def test_0020_website_search_data(self):
        """
        Tests that the auto-complete search URL returns JSON product data.
        """
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_client() as c:
            create_test_products()

            rv = c.get('/en/search-auto-complete?q=product')
            self.assertEqual(rv.status_code, 200)

            data = json.loads(rv.data.decode('utf-8'))

            self.assertEqual(data['results'], [])

    @with_transaction()
    def test_0030_website_menuitem(self):
        '''
        Test create menuitem for products
        '''
        pool = Pool()
        Product = pool.get('product.product')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_test_products()
        app = self.get_app()
        product, = Product.search([
                ('name', '=', 'Product 2'),
                    ])
        with app.test_request_context('/en/'):
            rv = product.get_menu_item(max_depth=10)
        self.assertEqual(rv['title'], product.name)

    @with_transaction()
    def test_0110_tree_node_menu_items(self):
        """
        Test to return record of tree node
        """
        pool = Pool()
        Company = pool.get('company.company')
        Node = pool.get('product.tree_node')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        default_node, = Node.create([{
            'name': 'root',
            'slug': 'root',
            'type_': 'catalog',
        }])
        node, = Node.create([{
            'name': 'Node1',
            'type_': 'catalog',
            'slug': 'node1',
            'parent': default_node,
        }])

        app = self.get_app()
        with app.test_request_context('/'):
            rv = node.get_menu_item(max_depth=10)
        self.assertEqual(rv['title'], node.name)

    @with_transaction()
    def test_0120_tree_get_tree_node_children(self):
        """
        Test children of tree node
        """
        pool = Pool()
        Product = pool.get('product.product')
        Node = pool.get('product.tree_node')
        ProductNodeRelationship = pool.get('product.product-product.tree_node')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_test_products()
        product, = Product.search([
                ('name', '=', 'Product 2'),
                    ])

        parent_node, = Node.create([{
            'name': 'node1',
            'slug': 'node1',
            'product_as_menu_children': False,
        }])
        child_node1, = Node.create([{
            'name': 'node1',
            'slug': 'node1',
            'product_as_menu_children': False,
            'parent': parent_node.id,
        }])
        child_node2, = Node.create([{
            'name': 'node2',
            'slug': 'node2',
            'product_as_menu_children': False,
            'parent': parent_node.id,
        }])
        ProductNodeRelationship.create([{
            'product': product.id,
            'node': parent_node.id,
            'sequence': 10,
        }])

        app = self.get_app()
        with app.test_request_context('/'):
            rv = parent_node.get_menu_item(max_depth=10)
        self.assertEqual(len(rv['children']), 2)

    @with_transaction()
    def test_0130_tree_get_tree_node_children_as_products(self):
        """
        Test if children of tree node are products
        """
        pool = Pool()
        Product = pool.get('product.product')
        Node = pool.get('product.tree_node')
        ProductNodeRelationship = pool.get('product.product-product.tree_node')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_test_products()
        product, = Product.search([
                ('name', '=', 'Product 2'),
                    ])
        node1, = Node.create([{
            'name': 'node1',
            'slug': 'node1',
            'product_as_menu_children': True,
        }])
        ProductNodeRelationship.create([{
            'product': product.id,
            'node': node1.id,
            'sequence': 10,
        }])

        app = self.get_app()
        with app.test_request_context('/'):
            rv = node1.get_menu_item(max_depth=10)
        self.assertEqual(len(rv['children']), 1)

    @with_transaction()
    def test_0210_templates_home_template(self):
        """
        Test for home template.
        """
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(request.path, '/en/')

    @with_transaction()
    def test_0215_templates_login(self):
        """
        Test for login template.
        """
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(request.path, '/en/')
            rv = c.get('/en/login')
            self.assertEqual(rv.status_code, 200)

            rv2 = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    }
                )
            self.assertEqual(rv2.status_code, 302)  # Login success

            self.assertIn('Redirecting', rv2.data.decode('utf-8'))
            self.assertTrue(rv2.location.endswith('/en/'))

            rv3 = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'pass wrong',
                    }
                )
            # Redirect to the login page
            self.assertEqual(rv2.status_code, 302)
            self.assertIn('<title>Nereid Webshop | Login</title>',
                rv3.data.decode('utf-8'))

    @with_transaction()
    def test_0220_templates_registration(self):
        """
        Test for registration template.
        """
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/registration')
            self.assertEqual(rv.status_code, 200)

            data = {
                'name': 'Registered User',
                'email': 'regd_user@m9s.biz',
                'password': 'password'
            }

            response = c.post('/en/registration', data=data)
            self.assertEqual(response.status_code, 200)

            data['confirm'] = 'password'
            response = c.post('/en/registration', data=data)
            self.assertEqual(response.status_code, 302)

    @with_transaction()
    def test_0225_templates_nodes(self):
        """
        Tests for nodes/subnodes.
        Tests node properties.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Node = pool.get('product.tree_node')
        Product = pool.get('product.product')
        ProductNodeRelationship = pool.get('product.product-product.tree_node')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        node1, = Node.create([{
            'name': 'Node1',
            'type_': 'catalog',
            'slug': 'node1',
        }])
        node2, = Node.create([{
            'name': 'Node2',
            'type_': 'catalog',
            'slug': 'node2',
            'display': 'product.template',
        }])
        node3, = Node.create([{
            'name': 'Node3',
            'type_': 'catalog',
            'slug': 'node3',
        }])

        Node.write([node2], {
            'parent': node1
        })
        Node.write([node3], {
            'parent': node2
        })

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])
        product2, = Product.search([
                ('name', '=', 'Product 2'),
                    ])
        product3, = Product.search([
                ('name', '=', 'Product 3'),
                    ])

        # Create Product-Node relationships.
        ProductNodeRelationship.create([{
                    'product': product1,
                    'node': node1,
                    }])
        ProductNodeRelationship.create([{
                    'product': product2,
                    'node': node2,
                    }])
        ProductNodeRelationship.create([{
                    'product': product3,
                    'node': node3,
                    }])

        for node in [node1, node2, node3]:
            self.assertTrue(node)

        self.assertEqual(node2.parent, node1)

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            url = '/en/nodes/{0}/{1}/{2}'.format(
                node1.id, node1.slug, 1
            )
            rv = c.get(url)
            self.assertEqual(rv.status_code, 200)

            url = '/en/nodes/{0}/{1}/{2}'.format(
                node2.id, node2.slug, 1
            )
            rv = c.get(url)
            self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0230_templates_articles(self):
        """
        Tests the rendering of an article.
        """
        pool = Pool()
        ArticleCategory = pool.get('nereid.cms.article.category')
        Article = pool.get('nereid.cms.article')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        # Create an article category
        categ, = ArticleCategory.create([{
            'title': 'Test Categ',
            'unique_name': 'test-categ',
        }])

        article, = Article.create([{
            'title': 'Test Article',
            'uri': 'test-article',
            'content': 'Test Content',
            'sequence': 10,
            'categories': [('add', [categ.id])],
        }])

        self.assertEqual(len(categ.published_articles), 0)
        Article.publish([article])
        self.assertEqual(len(categ.published_articles), 1)

        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en/article/test-article')
            self.assertEqual(response.status_code, 200)
            self.assertIn('Test Content', response.data.decode('utf-8'))
            self.assertIn('Test Article', response.data.decode('utf-8'))

    @with_transaction()
    def test_0235_templates_cart_guest(self):
        """
        Test the cart without login
        """
        pool = Pool()
        Company = pool.get('company.company')
        Product = pool.get('product.product')
        Sale = pool.get('sale.sale')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])

        qty = 7
        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            sales = Sale.search([])
            self.assertEqual(len(sales), 0)

            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': qty,
                    })

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            sales = Sale.search([])
            self.assertEqual(len(sales), 1)
            sale = sales[0]
            self.assertEqual(len(sale.lines), 1)
            self.assertEqual(
                sale.lines[0].product, product1)
            self.assertEqual(sale.lines[0].quantity, qty)

    @with_transaction()
    def test_0238_templates_cart_logged_in(self):
        """
        Test the cart with login
        """
        pool = Pool()
        Company = pool.get('company.company')
        Product = pool.get('product.product')
        Sale = pool.get('sale.sale')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])

        qty = 7
        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    }
                )
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            sales = Sale.search([])
            self.assertEqual(len(sales), 0)

            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': qty,
                    })

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            sales = Sale.search([])
            self.assertEqual(len(sales), 1)
            sale = sales[0]
            self.assertEqual(len(sale.lines), 1)
            self.assertEqual(
                sale.lines[0].product, product1)
            self.assertEqual(sale.lines[0].quantity, qty)

    @with_transaction()
    def test_0240_templates_addresses(self):
        """
        Test addresses.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Address = pool.get('party.address')
        SaleConfiguration = pool.get('sale.configuration')
        NereidUser = pool.get('nereid.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/view-address')
            self.assertEqual(rv.status_code, 302)

            response = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    }
                )
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.get('/en/view-address')
            self.assertEqual(rv.status_code, 200)

            # Creating an address
            rv = c.get('/en/create-address')
            self.assertEqual(rv.status_code, 200)

            data = {
                'name': 'Some Dude',
                'street': 'Fancy Test Street',
                'postal_code': 'postal_code123',
                'city': 'Bigcity',
                'email': 'info@m9s.biz',
                'phone': '123456789',
                'country': country.id,
                'subdivision': subdivision.id,
                }

            # Check if only one address from setup before posting
            self.assertEqual(
                len(registered_user.party.addresses), 1)

            response = c.post('/en/create-address',
                data=data)
            self.assertEqual(response.status_code, 302)

            # Check that our address info is present in template data.
            rv = c.get('/en/view-address')
            self.assertIn(data['name'], rv.data.decode('utf-8'))
            self.assertIn(data['street'], rv.data.decode('utf-8'))
            self.assertIn(data['city'], rv.data.decode('utf-8'))

            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                len(registered_user.party.addresses), 2)

            # Now edit some bits of the address and view it again.
            address, = Address.search([
                    ('party_name', '=', data['name']),
                    ('party', '=', registered_user.party.id),
                    ])
            rv = c.get('/en/edit-address/{0}'.format(address.id))
            self.assertEqual(rv.status_code, 200)

            response = c.post('/en/edit-address/{0}'.format(address.id),
                data={
                    'name': 'Some Other Dude',
                    'street': 'Street',
                    'postal_code': 'postal_code',
                    'city': 'City',
                    'email': 'info@m9s.biz',
                    'phone': '1234567890',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    })
            self.assertEqual(response.status_code, 302)

            rv = c.get('/en/view-address')
            self.assertIn('Some Other Dude', rv.data.decode('utf-8'))
            with self.assertRaises(AssertionError):
                self.assertIn(data['name'], rv.data.decode('utf-8'))

            # Now remove the address.
            rv = c.post('/en/remove-address/{0}'.format(address.id))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                len(registered_user.party.addresses), 1)

    @with_transaction()
    def test_0245_templates_wishlist(self):
        """
        Tests the wishlist.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        SaleConfiguration = pool.get('sale.configuration')
        NereidUser = pool.get('nereid.user')
        Product = pool.get('product.product')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])
        product2, = Product.search([
                ('name', '=', 'Product 2'),
                    ])

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            # Guests will be redirected.
            rv = c.post(
                '/en/wishlists',
                data={
                    'name': 'Testlist'
                }
            )
            self.assertEqual(rv.status_code, 302)

            response = c.post(
                '/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    }
                )
            self.assertEqual(response.status_code, 302)  # Login success

            # No wishlists currently.
            self.assertEqual(
                len(registered_user.wishlists),
                0
            )
            rv = c.post(
                '/en/wishlists',
                data={
                    'name': 'Testlist'
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                len(registered_user.wishlists),
                1
            )
            rv = c.get('/en/wishlists')
            self.assertIn('Testlist', rv.data.decode('utf-8'))

            # Remove this wishlist.
            rv = c.delete(
                '/en/wishlists/{0}'.format(
                    registered_user.wishlists[0].id
                )
            )
            self.assertEqual(rv.status_code, 200)

            # Adding a product without creating a wishlist
            # creates a wishlist automatically.
            rv = c.post(
                '/en/wishlists/products',
                data={
                    'product': product1.id,
                    'action': 'add'
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(len(registered_user.wishlists), 1)
            self.assertEqual(
                len(registered_user.wishlists[0].products),
                1
            )
            rv = c.get(
                '/en/wishlists/{0}'
                .format(registered_user.wishlists[0].id)
            )
            self.assertIn(product1.name, rv.data.decode('utf-8'))

            # Add another product.
            rv = c.post(
                '/en/wishlists/products',
                data={
                    'product': product2.id,
                    'action': 'add',
                    'wishlist': registered_user.wishlists[0].id
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                len(registered_user.wishlists[0].products),
                2
            )

            rv = c.get(
                '/en/wishlists/{0}'
                .format(registered_user.wishlists[0].id)
            )
            self.assertIn(product2.name, rv.data.decode('utf-8'))

            # Remove a product
            rv = c.post(
                '/en/wishlists/products',
                data={
                    'product': product2.id,
                    'wishlist': registered_user.wishlists[0].id,
                    'action': 'remove'
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                len(registered_user.wishlists[0].products),
                1
            )

            rv = c.get(
                '/en/wishlists/{0}'
                .format(registered_user.wishlists[0].id)
            )
            self.assertNotIn(product2.name, rv.data.decode('utf-8'))

    @with_transaction()
    def test_0255_templates_guest_checkout(self):
        """
        Test for guest checkout.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Sale = pool.get('sale.sale')
        SaleConfiguration = pool.get('sale.configuration')
        NereidUser = pool.get('nereid.user')
        NereidWebsite = pool.get('nereid.website')
        Product = pool.get('product.product')
        Account = pool.get('account.account')
        Party = pool.get('party.party')
        User = pool.get('res.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])
        # Activate the user to block the email for others
        registered_user.active = True
        registered_user.email_verified = True
        registered_user.save()

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])
        product2, = Product.search([
                ('name', '=', 'Product 2'),
                    ])

        User.set_preferences({'current_channel': website.channel})
        User.write(
            [User(USER)], {
                'company': company.id,
                'current_channel': website.channel,
                })

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.post(
                '/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 5
                }
            )
            self.assertEqual(rv.status_code, 302)

            rv = c.get('/en/checkout/sign-in')
            self.assertEqual(rv.status_code, 200)

            # Trying to checkout with a registered email should fail
            rv = c.post(
                '/en/checkout/sign-in',
                data={
                    'email': 'info@m9s.biz'
                }
            )
            self.assertEqual(rv.status_code, 200)
            self.assertIn('{0}'.format(registered_user.email),
                rv.data.decode('utf-8'))
            self.assertIn(
                'is already registered with an existing account',
                rv.data.decode('utf-8'))
            # Now with a new email
            rv = c.post(
                '/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest'
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/checkout/shipping-address')
            )

            # Shipping address page should render
            rv = c.get('/en/checkout/shipping-address')
            self.assertEqual(rv.status_code, 200)

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'postal_code': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
                'phone': '+491791234567',
            }
            # Shipping address
            rv = c.post(
                '/en/checkout/shipping-address',
                data=address_data)
            # 200 ususally means failing address form validation
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/checkout/validate-address'))

            # Billing address
            rv = c.post(
                '/en/checkout/billing-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'postal_code': '682013',
                    'city': 'Cochin',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    'phone': '+491791234567',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/checkout/delivery-method'))

            # Delivery method
            rv = c.post('/en/checkout/delivery-method',
                data={})
            # Should per default stay on delivery-method if no carrier was
            # provided
            self.assertEqual(rv.status_code, 200)
            # Check for the missing carrier selection
            self.assertIn('No shipping method found', rv.data.decode('utf-8'))
            # Check for the flash message if delievery-method was posted
            # nevertheless
            self.assertIn(
                'There was no carrier selected', rv.data.decode('utf-8'))

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                # Set default receivable account
                receivable, = Account.search([
                        ('type.receivable', '=', True),
                        ])
                parties = Party.search([])
                Party.write(parties, {
                        'account_receivable': receivable,
                        })

                # Try to pay using credit card
                card_data = {
                    'owner': 'Joe Blow',
                    'number': '4111111111111111',
                    'expiry_year': '2030',
                    'expiry_month': '01',
                    'cvv': '911',
                    'add_card_to_profiles': '',
                    }
                rv = c.post(
                    '/en/checkout/payment',
                    data=card_data)

                # Run the sale and payment processing usually delegated
                # to the queue
                sale, = Sale.search([])
                Sale.quote_web_sales([sale])

                self.assertEqual(sale.state, 'quotation')
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)

                rv = c.get('/en/order/{0}'.format(sale.id))
                self.assertEqual(rv.status_code, 302)  # Orders page redirect

    @with_transaction()
    def test_0260_templates_registered_checkout(self):
        """
        Test for registered user checkout.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Sale = pool.get('sale.sale')
        SaleConfiguration = pool.get('sale.configuration')
        NereidUser = pool.get('nereid.user')
        NereidWebsite = pool.get('nereid.website')
        Product = pool.get('product.product')
        Account = pool.get('account.account')
        Party = pool.get('party.party')
        User = pool.get('res.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])
        product2, = Product.search([
                ('name', '=', 'Product 2'),
                    ])

        User.set_preferences({'current_channel': website.channel})
        User.write(
            [User(USER)], {
                'company': company.id,
                'current_channel': website.channel,
                })

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.post(
                '/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 5
                }
            )
            self.assertEqual(rv.status_code, 302)

            # Now sign in to checkout.
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    'checkout_mode': 'account'
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/shipping-address'))

            # Shipping address page should render
            rv = c.get('/en/checkout/shipping-address')
            self.assertEqual(rv.status_code, 200)

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'postal_code': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
                'phone': '+491791234567',
            }
            # Shipping address
            rv = c.post(
                '/en/checkout/shipping-address',
                data=address_data)
            # 200 ususally means failing address form validation
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/checkout/validate-address'))

            # Billing address
            rv = c.post(
                '/en/checkout/billing-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'postal_code': '682013',
                    'city': 'Cochin',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    'phone': '+491791234567',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/checkout/delivery-method'))

            # Delivery method
            rv = c.post('/en/checkout/delivery-method',
                data={})
            # Should per default stay on delivery-method if no carrier was
            # provided
            self.assertEqual(rv.status_code, 200)
            # Check for the missing carrier selection
            self.assertIn('No shipping method found', rv.data.decode('utf-8'))
            # Check for the flash message if delievery-method was posted
            # nevertheless
            self.assertIn(
                'There was no carrier selected', rv.data.decode('utf-8'))

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                # Set default receivable account
                receivable, = Account.search([
                        ('type.receivable', '=', True),
                        ])
                parties = Party.search([])
                Party.write(parties, {
                        'account_receivable': receivable,
                        })

                # Try to pay using credit card
                card_data = {
                    'owner': 'Joe Blow',
                    'number': '4111111111111111',
                    'expiry_year': '2030',
                    'expiry_month': '01',
                    'cvv': '911',
                    'add_card_to_profiles': '',
                    }
                rv = c.post(
                    '/en/checkout/payment',
                    data=card_data)

                # Run the sale and payment processing usually delegated
                # to the queue
                sale, = Sale.search([])
                Sale.quote_web_sales([sale])

                self.assertEqual(sale.state, 'quotation')
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)

                rv = c.get('/en/order/{0}?access_code={1}'.format(
                        sale.id, sale.guest_access_code))
                self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0265_templates_password_reset(self):
        """
        Test for password reset.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        app = self.get_app()
        with app.test_client() as c:
            # Resetting without login
            rv = c.get('/en/reset-account')
            self.assertEqual(rv.status_code, 200)

            # Resetting through email
            response = c.post(
                '/en/reset-account',
                data={
                    'email': 'info@m9s.biz'
                    })
            self.assertEqual(response.status_code, 302)

            # Login still possible after requesting activation code
            rv = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password'
                    })
            self.assertEqual(rv.status_code, 302)

        # Reset properly
        with app.test_client() as c:
            response = c.post('/en/reset-account',
                data={
                    'email': 'info@m9s.biz'
                    })
            self.assertEqual(response.status_code, 302)

            # Resetting with an invalid code.
            # Login with new pass should be rejected.
            invalid_code = 'badcode'
            response = c.post(
                '/en/new-password/{0}/{1}'.format(
                    registered_user.id, invalid_code),
                data={
                    'password': 'reset-pass',
                    'confirm': 'reset-pass'
                    })
            self.assertEqual(response.status_code, 302)

            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'reset-pass'
                    })
            # Rejection
            self.assertEqual(response.status_code, 200)

            # Now do it with the correct code
            # Note: the password validation now requires a complex password
            new_pass = '9ReaLyComPlexPAsSWrd'
            response = c.post(
                registered_user.get_reset_password_link(),
                data={
                    'password': new_pass,
                    'confirm': new_pass,
                    })
            self.assertEqual(response.status_code, 302)

            # This time, login with old pass should be rejected.
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password'
                    })
            self.assertEqual(response.status_code, 200)

            # Login with the correct code
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': new_pass,
                    })
            self.assertEqual(rv.status_code, 302)

    @with_transaction()
    def test_0270_templates_change_password(self):
        """
        Test for password change.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        original_pass = 'password'
        new_pass = '9ReaLyComPlexPAsSWrd'

        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en/change-password')
            # Without login
            self.assertEqual(response.status_code, 302)

            # Try POST, but without login
            response = c.post('/en/change-password', data={
                'password': original_pass,
                'confirm': original_pass
            })
            self.assertEqual(response.status_code, 302)

            # Now login
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': original_pass,
                    })

            # Incorrect password confirmation
            response = c.post('/en/change-password',
                data={
                    'password': new_pass,
                    'confirm': 'oh-no-you-dont'
                    })
            self.assertEqual(response.status_code, 200)
            self.assertTrue("must match" in response.data.decode('utf-8'))

            # Send proper confirmation but without old password.
            response = c.post('/en/change-password',
                data={
                    'password': new_pass,
                    'confirm': new_pass
                    })
            self.assertEqual(response.status_code, 200)

            # Send proper confirmation with wrong old password
            response = c.post('/en/change-password',
                data={
                    'old_password': 'passw',
                    'password': new_pass,
                    'confirm': new_pass,
                    })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                'current password you entered is invalid'
                in response.data.decode('utf-8'))

            # Do it right
            response = c.post('/en/change-password',
                data={
                    'old_password': original_pass,
                    'password': new_pass,
                    'confirm': new_pass,
                    })
            self.assertEqual(response.status_code, 302)

            # Check login with new pass
            c.get('/en/logout')
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': new_pass,
                    })

    @with_transaction()
    def test_0275_templates_products(self):
        """
        Tests product templates and variants.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        ProductTemplate = pool.get('product.template')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            create_test_products()

            template1, = ProductTemplate.search([
                    ('name', '=', 'Product 1'),
                    ])

            rv = c.get('/en/products')
            self.assertIn('Product 1', rv.data.decode('utf-8'))
            self.assertIn('Product 2', rv.data.decode('utf-8'))
            self.assertIn('Product 3', rv.data.decode('utf-8'))

            rv = c.get('/en/product/product-1')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Product 1', rv.data.decode('utf-8'))

            for product in template1.products:
                product.active = False
                product.save()
            template1.active = False
            template1.save()

            rv = c.get('/en/product/product-1')
            self.assertEqual(rv.status_code, 404)

    @with_transaction()
    def test_0280_templates_search_results(self):
        """
        Test the search results template.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            create_test_products()

            rv = c.get('/en/search?q=product')
            self.assertIn('Product 1', rv.data.decode('utf-8'))
            self.assertIn('product-1', rv.data.decode('utf-8'))
            self.assertIn('Product 2', rv.data.decode('utf-8'))
            self.assertIn('product-2', rv.data.decode('utf-8'))
            self.assertIn('Product 3', rv.data.decode('utf-8'))
            self.assertIn('product-3', rv.data.decode('utf-8'))

    @with_transaction()
    def test_0290_templates_product_inventory(self):
        """
        Tests the product template for cases of 'In Stock', 'Out Of Stock' and
        'X <uom>s available'.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        ProductTemplate = pool.get('product.template')
        StockMove = pool.get('stock.move')
        Location = pool.get('stock.location')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        del self.templates['product.jinja']

        with Transaction().set_context(company=company.id):
            create_test_products()
            template1, = ProductTemplate.search([
                ('name', '=', 'Product 1')
            ])
            product1 = template1.products[0]

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_request_context('/'):
            # Check serialize method
            res = product1.serialize(purpose='variant_selection')
            self.assertIn('inventory_status', res)

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')

            # No inventory made yet, and product is goods type
            self.assertIn('In stock', rv.data.decode('utf-8'))

            # Let's create inventory
            supplier, = Location.search([('code', '=', 'SUP')])
            stock1, = StockMove.create([{
                'product': product1.id,
                'unit': template1.sale_uom.id,
                'quantity': 10,
                'from_location': supplier,
                'to_location': website.stock_location.id,
                'company': website.company.id,
                'unit_price': Decimal('1'),
                'cost_price': Decimal('1'),
                'currency': website.currencies[0].id,
                'planned_date': date.today(),
                'effective_date': date.today(),
                'state': 'draft',
            }])
            StockMove.write([stock1], {
                'state': 'done'
            })

            product1.display_available_quantity = True
            product1.start_displaying_available_quantity = 10
            product1.min_warehouse_quantity = 5
            product1.save()

        # min_warehouse_quantity < quantity <= start_displaying
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')

            # X <uom> available
            self.assertIn(
                str(
                    product1.get_availability().get('quantity') -
                    product1.min_warehouse_quantity
                ) +
                ' ' + product1.default_uom.name,
                rv.data.decode('utf-8')
            )

        product1.start_displaying_available_quantity = 3
        product1.save()

        # min_warehouse_quantity < quantity
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')

            # In Stock
            self.assertIn('In stock', rv.data.decode('utf-8'))

        product1.min_warehouse_quantity = 11
        product1.save()

        # min_warehouse_quantity > quantity
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')

            # Out Of Stock
            self.assertIn('Out of stock', rv.data.decode('utf-8'))

        product1.min_warehouse_quantity = 0
        product1.save()

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')

            # Only in stock and out of stock cases
            self.assertIn('In stock', rv.data.decode('utf-8'))

        product1.min_warehouse_quantity = -1
        product1.save()

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')

            # Always in stock
            self.assertIn('In stock', rv.data.decode('utf-8'))

    def test_0300_css(self):
        """
        Test for CSS validation using W3C standards.
        """
        cssfile = join(css_dir, 'style.css')
        validate_css(cssfile)

    @with_transaction()
    def test_0410_gift_card_render_on_website(self):
        """
        Test the rendering of gift card on website
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        gift_card_product = create_product(is_gift_card=True)
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        product = create_product(is_gift_card=False)
        product.displayed_on_eshop = True
        product.uri = "test-product"
        product.save()

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/product/%s' % gift_card_product.uri)
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/gift-card/gift-card-product')
            )

            rv = c.get('/en/product/%s' % product.uri)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), product.name)

    @with_transaction()
    def test_0420_gift_card_add_to_cart_wo_open_amount(self):
        """
        Test adding gift card without open amounts
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(
            is_gift_card=True, type="service", mode="virtual"
        )
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()

        with app.test_client() as c:
            data = {
                'recipient_email': 'rec@m9s.biz',
                'recipient_name': 'Recipient',
                'selected_amount': gift_card_product.gift_card_prices[0].id,
                'open_amount': 0.0,
                'message': 'Test Message',
            }
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,500.00' % Cart.find_cart().id)

            # Test login handler
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            cart = Cart.find_cart(user=registered_user.id)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,500.00' % cart.id)

            # Test if a new line is added if the same gift card
            # is added to cart
            c.post('/en/gift-card/%s' % gift_card_product.uri,
                data=data)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'),
                'Cart:%d,2,1000.00' % cart.id)

    @with_transaction()
    def test_0430_gift_card_add_to_cart_with_open_amount(self):
        """
        Test adding gift card with open amounts
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(
            is_gift_card=True, type="service", mode="virtual",
            allow_open_amount=True)
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()
        with app.test_client() as c:
            data = {
                'recipient_email': 'rec@m9s.biz',
                'recipient_name': 'Recipient',
                'selected_amount': 0,
                'open_amount': 200,
                'message': 'Test Message',
            }
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,200.00' % Cart.find_cart().id)

            # Test login handler
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            cart = Cart.find_cart(user=registered_user.id)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,200.00' % cart.id)

            # Test if a new line is added if the same gift card
            # is added to cart
            c.post('/en/gift-card/%s' % gift_card_product.uri,
                data=data)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'),
                'Cart:%d,2,400.00' % cart.id)

    @with_transaction()
    def test_0440_gift_card_add_to_cart_check_open_amount(self):
        """
        Test adding gift card with not allowed open amount
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(
            is_gift_card=True, type="service", mode="virtual",
            allow_open_amount=True
        )
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()
        with app.test_client() as c:
            data = {
                'recipient_email': 'rec@m9s.biz',
                'recipient_name': 'Recipient',
                'selected_amount': 0,
                'open_amount': 500,
                'message': 'Test Message',
            }

            # Test if nothing was added to cart because open amount is
            # not defined within the allowed range
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertFalse(Cart.search([]))

    @with_transaction()
    def test_0450_gift_card_add_to_cart_physical_selected_amount(self):
        """
        Test adding physical gift card with selected amounts
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(is_gift_card=True)
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()
        with app.test_client() as c:
            data = {
                'recipient_email': 'rec@m9s.biz',
                'recipient_name': 'Recipient',
                'selected_amount': gift_card_product.gift_card_prices[0].id,
                'open_amount': 0.0,
                'message': 'Test Message',
            }
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,500.00' % Cart.find_cart().id)

            # Test login handler
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            cart = Cart.find_cart(user=registered_user.id)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,500.00' % cart.id)

            # Test if a new line is added if the same gift card
            # is added to cart
            c.post('/en/gift-card/%s' % gift_card_product.uri,
                data=data)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'),
                'Cart:%d,2,1000.00' % cart.id)

    @with_transaction()
    def test_0460_gift_card_add_to_cart_physical_open_amount(self):
        """
        Test adding physical gift card with open amounts
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(
            is_gift_card=True, allow_open_amount=True)
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()
        with app.test_client() as c:
            data = {
                'selected_amount': 0,
                'open_amount': 200.0,
                'message': 'Test Message',
            }
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,200.00' % Cart.find_cart().id)

            # Test login handler
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            cart = Cart.find_cart(user=registered_user.id)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,200.00' % cart.id)

            # Test if a new line is added if the same gift card
            # is added to cart
            c.post('/en/gift-card/%s' % gift_card_product.uri,
                data=data)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'),
                'Cart:%d,2,400.00' % cart.id)

    @with_transaction()
    def test_0470_gift_card_add_to_cart_combined_selected_amount(self):
        """
        Test adding combined gift card with selected amounts
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(is_gift_card=True, mode='combined')
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()
        with app.test_client() as c:
            data = {
                'recipient_email': 'rec@m9s.biz',
                'selected_amount': gift_card_product.gift_card_prices[0].id,
                'open_amount': 0.0,
                'message': 'Test Message',
            }
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,500.00' % Cart.find_cart().id)

            # Test login handler
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            cart = Cart.find_cart(user=registered_user.id)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,500.00' % cart.id)

            # Test if a new line is added if the same gift card
            # is added to cart
            c.post('/en/gift-card/%s' % gift_card_product.uri,
                data=data)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'),
                'Cart:%d,2,1000.00' % cart.id)

    @with_transaction()
    def test_0480_gift_card_add_to_cart_combined_with_open_amount(self):
        """
        Test adding combined gift card with open amounts
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Cart = pool.get('nereid.cart')
        NereidUser = pool.get('nereid.user')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        gift_card_product = create_product(
            is_gift_card=True, mode='combined', allow_open_amount=True)
        gift_card_product.displayed_on_eshop = True
        gift_card_product.uri = "gift-card-product"
        gift_card_product.save()

        app = self.get_app()
        with app.test_client() as c:
            data = {
                'recipient_email': 'rec@m9s.biz',
                'recipient_name': 'Recipient',
                'selected_amount': 0,
                'open_amount': 200,
                'message': 'Test Message',
            }
            c.post(
                '/en/gift-card/%s' % gift_card_product.uri, data=data
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,200.00' % Cart.find_cart().id)

            # Test login handler
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            cart = Cart.find_cart(user=registered_user.id)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'),
                'Cart:%d,1,200.00' % cart.id)

            # Test if a new line is added if the same gift card
            # is added to cart
            c.post('/en/gift-card/%s' % gift_card_product.uri,
                data=data)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'),
                'Cart:%d,2,400.00' % cart.id)

    @with_transaction()
    def test_0510_download_invoice(self):
        """
        Test to download invoice from a sale
        """
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        Sale = pool.get('sale.sale')
        SaleConfiguration = pool.get('sale.configuration')
        NereidUser = pool.get('nereid.user')
        NereidWebsite = pool.get('nereid.website')
        Product = pool.get('product.product')
        Account = pool.get('account.account')
        Party = pool.get('party.party')
        User = pool.get('res.user')
        Invoice = pool.get('account.invoice')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway(method='dummy')
        gateway.save()
        company, = Company.search([])

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        registered_user, = NereidUser.search([
                ('email', '=', 'info@m9s.biz'),
                ])

        create_test_products()
        product1, = Product.search([
                ('name', '=', 'Product 1'),
                    ])
        product2, = Product.search([
                ('name', '=', 'Product 2'),
                    ])

        User.set_preferences({'current_channel': website.channel})
        User.write(
            [User(USER)], {
                'company': company.id,
                'current_channel': website.channel,
                })

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        app = self.get_app()
        context = {
            'company': company.id,
            'use_dummy': True,
            'dummy_succeed': True,
            }
        with Transaction().set_context(**context), \
            app.test_client() as c:
            rv = c.post(
                '/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 5
                }
            )
            self.assertEqual(rv.status_code, 302)

            # Now sign in to checkout.
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    'checkout_mode': 'account'
                }
            )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/shipping-address'))

            # Shipping address page should render
            rv = c.get('/en/checkout/shipping-address')
            self.assertEqual(rv.status_code, 200)

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'postal_code': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
                'phone': '+491791234567',
            }
            # Shipping address
            rv = c.post(
                '/en/checkout/shipping-address',
                data=address_data)
            # 200 ususally means failing address form validation
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/checkout/validate-address'))

            # Billing address
            rv = c.post(
                '/en/checkout/billing-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'postal_code': '682013',
                    'city': 'Cochin',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    'phone': '+491791234567',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/checkout/delivery-method'))

            # Delivery method
            rv = c.post('/en/checkout/delivery-method',
                data={})
            # Should per default stay on delivery-method if no carrier was
            # provided
            self.assertEqual(rv.status_code, 200)
            # Check for the missing carrier selection
            self.assertIn('No shipping method found', rv.data.decode('utf-8'))
            # Check for the flash message if delievery-method was posted
            # nevertheless
            self.assertIn(
                'There was no carrier selected', rv.data.decode('utf-8'))

            # Set default receivable account
            receivable, = Account.search([
                    ('type.receivable', '=', True),
                    ])
            parties = Party.search([])
            Party.write(parties, {
                    'account_receivable': receivable,
                    })

            # Try to pay using credit card
            card_data = {
                'owner': 'Joe Blow',
                'number': '4111111111111111',
                'expiry_year': '2030',
                'expiry_month': '01',
                'cvv': '911',
                'add_card_to_profiles': '',
                }
            rv = c.post(
                '/en/checkout/payment',
                data=card_data)

            # Run the sale and payment processing usually delegated
            # to the queue
            sale, = Sale.search([])
            Sale.quote_web_sales([sale])

            self.assertEqual(sale.state, 'quotation')
            payment_transaction, = sale.gateway_transactions
            self.assertEqual(payment_transaction.amount, sale.total_amount)

            rv = c.get('/en/order/{0}?access_code={1}'.format(
                    sale.id, sale.guest_access_code))
            self.assertEqual(rv.status_code, 200)

            Sale.process_all_pending_payments()
            Sale.confirm([sale])
            Sale.process_all_pending_payments()
            Sale.process([sale])
            Invoice.post(sale.invoices)

            # Logged in user tries to download invoice
            rv = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password'
                    })
            response = c.get(
                '/en/orders/invoice/%s/download' % (sale.invoices[0].id,))


del NereidModuleTestCase
