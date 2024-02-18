# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import datetime
import json

from decimal import Decimal

import pycountry

from dateutil.relativedelta import relativedelta
from werkzeug.datastructures import Headers

from trytond.config import config
from trytond.modules.company.tests import (CompanyTestMixin,
    create_company, set_company)
from trytond.modules.nereid_base.tests.common import (
    create_static_file, create_website_locale)
from trytond.modules.payment_gateway.tests import (
    create_payment_gateway, create_payment_profile)
from trytond.modules.sale_channel_price_list.tests.test_module import (
    create_channel_sale, create_sale_channels)
from trytond.pool import Pool
from trytond.tests.test_tryton import USER
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

from nereid import current_website
from nereid.globals import session
from nereid.testing import NereidModuleTestCase

config.set('database', 'path', '/tmp')


def create_website(name='localhost', locales=[], default_locale=None):
    """
    Creates the website for testing
    """
    pool = Pool()
    Website = pool.get('nereid.website')
    Party = pool.get('party.party')
    User = pool.get('res.user')
    UserCompany = pool.get('res.user-company.company')
    NereidUser = pool.get('nereid.user')
    Company = pool.get('company.company')
    SaleChannel = pool.get('sale.channel')
    Location = pool.get('stock.location')
    Currency = pool.get('currency.currency')

    websites = Website.search([('name', '=', name)])
    if websites:
        return websites[0]

    companies = Company.search([])
    if companies:
        company = companies[0]
    else:
        company = create_company()

    user = User(USER)
    user_company = UserCompany()
    user_company.company = company
    user_company.user = user
    user_company.save()
    user.company = company
    user.save()

    ctx = Transaction().context.copy()
    ctx.update(User.get_preferences(context_only=True))

    with set_company(company), Transaction().set_context(**ctx):
        create_sale_channels(company)
        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        User.set_preferences({'current_channel': channel1})
        channel_price_list, user_price_list = create_pricelists()

        warehouse, = Location.search([
                ('type', '=', 'warehouse'),
                ])
        channel1.price_list = channel_price_list
        channel1.invoice_method = 'order'
        channel1.shipment_method = 'order'
        channel1.source = 'webshop'
        channel1.warehouse = warehouse
        channel1.save()

        party1, = Party.create([{
            'name': 'Guest User',
        }])
        party2, = Party.create([{
            'name': 'Registered User 1',
            'sale_price_list': user_price_list,
            'addresses': [('create', [{
                'name': 'Address1',
            }])],
        }])
        party3, = Party.create([{
            'name': 'Registered User 2',
        }])

        guest_user, = NereidUser.create([{
            'party': party1.id,
            'name': 'Guest User',
            'email': 'guest@m9s.biz',
            'password': 'password',
            'company': company.id,
        }])
        registered_user, = NereidUser.create([{
            'party': party2.id,
            'name': 'Registered User',
            'email': 'info@m9s.biz',
            'password': 'password',
            'company': company.id,
        }])
        registered_user2, = NereidUser.create([{
            'party': party3.id,
            'name': 'Registered User 2',
            'email': 'mail@m9s.biz',
            'password': 'password2',
            'company': company.id,
        }])

        usd, = Currency.search([
                ('code', '=', 'usd'),
                ])

        if not locales:
            locale = create_website_locale()
            locales = [locale.id]
            default_locale = locale
        else:
            locales = [l for l in locales]

        if default_locale is None:
            default_locale = locales[0]

        website = Website()
        website.name = name
        website.company = company
        website.application_user = USER
        website.default_locale = default_locale
        website.locales = locales
        website.guest_user = guest_user
        website.channel = channel1
        website.currencies = [usd]
        return website


def create_countries(count=5):
    """
    Create some sample countries and subdivisions
    """
    pool = Pool()
    Subdivision = pool.get('country.subdivision')
    Country = pool.get('country.country')

    for country in list(pycountry.countries)[0:count]:
        countries = Country.create([{
            'name': country.name,
            'code': country.alpha_2,
        }])
        try:
            divisions = pycountry.subdivisions.get(
                country_code=country.alpha_2
            )
        except KeyError:
            pass
        else:
            for subdivision in list(divisions)[0:count]:
                Subdivision.create([{
                    'country': countries[0].id,
                    'name': subdivision.name,
                    'code': subdivision.code,
                    'type': subdivision.type.lower(),
                }])


def create_pricelists(party_pl_margin=None, guest_pl_margin=None):
    """
    Create the pricelists
    """
    pool = Pool()
    PriceList = pool.get('product.price_list')
    Company = pool.get('company.company')

    if party_pl_margin is None:
        party_pl_margin = Decimal('1.10')
    if guest_pl_margin is None:
        guest_pl_margin = Decimal('1.20')
    # Setup the pricelists
    company, = Company.search([])
    user_price_list, = PriceList.create([{
        'name': 'PL 1',
        'company': company.id,
        'price': 'list_price',
        'lines': [
            ('create', [{
                'formula': 'unit_price * %s' % party_pl_margin
            }])
        ],
    }])
    guest_price_list, = PriceList.create([{
        'name': 'PL 2',
        'company': company.id,
        'price': 'list_price',
        'lines': [
            ('create', [{
                'formula': 'unit_price * %s' % guest_pl_margin
            }])
        ],
    }])
    return guest_price_list.id, user_price_list.id


def create_product_template(name, vlist, uri, uom='Unit'):
    """
    Create a product template with products and return its ID

    :param name: Name of the product
    :param vlist: List of dictionaries of values to create
    :param uri: uri of product template
    :param uom: Note it is the name of UOM (not symbol or code)
    """
    pool = Pool()
    Template = pool.get('product.template')
    Category = pool.get('product.category')
    Uom = pool.get('product.uom')
    Account = pool.get('account.account')
    Company = pool.get('company.company')

    company, = Company.search([])
    with set_company(company), \
        Transaction().set_context(company=company.id):
        revenue, = Account.search([
                ('type.revenue', '=', True),
                ])
        expense, = Account.search([
                ('type.expense', '=', True),
                ])

        category = Category()
        category.name = 'Account category'
        category.account_revenue = revenue
        category.account_expense = expense
        category.accounting = True
        category.save()

        uom, = Uom.search([('name', '=', uom)])
        for values in vlist:
            values['name'] = name
            values['default_uom'] = uom
            values['sale_uom'] = uom
            values['account_category'] = category
            values['products'] = [
                ('create', [{
                    'uri': uri,
                    'displayed_on_eshop': True,
                    'cost_price': Decimal('5'),
                }])
            ]
        template = Template.create(vlist)
    return template


class NereidCartB2CTestCase(CompanyTestMixin, NereidModuleTestCase):
    'Test Nereid Cart B2C module'
    module = 'nereid_cart_b2c'
    extras = ['sale_payment_gateway']

    def setUp(self):
        self.templates = {
            'home.jinja': '{{get_flashed_messages()}}',
            'login.jinja':
                '{{ login_form.errors }} {{get_flashed_messages()}}',
            'shopping-cart.jinja':
                'Cart:{{ cart.id }},{{get_cart_size()|round|int}},'
                '{{cart.sale.total_amount}}',
            #'product.jinja':
            #    '{{ product.sale_price(product.id) }}',
            'product.jinja':
                '{{ product.sale_price(1) }}',
            }

    @with_transaction()
    def test_0005_cart_json(self):
        """
        Test that `cart.json` returns a dictionary
        with correct params.
        """
        pool = Pool()
        Company = pool.get('company.company')
        SaleLine = pool.get('sale.line')
        Product = pool.get('product.product')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

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

            product, = Product.search([('name', '=', 'product-1')])

            rv = c.post(
                '/en/cart/add',
                data={
                    'product': product.id, 'quantity': 7
                }
            )
            self.assertEqual(rv.status_code, 302)

            results = c.get('/en/cart.json')
            data = json.loads(results.data)
            lines = data['cart']['lines']

            self.assertEqual(len(lines), 1)
            line, = SaleLine.search([])
            self.assertEqual(line.serialize('cart'), lines[0])

    @with_transaction()
    def test_0010_test_guest_price(self):
        """
        Test the pricelist lookup algorithm

        We are not logged in, the pricelist of the channel is used.
        """
        pool = Pool()
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        guest_pl_margin = Decimal('1.20')

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product/product-1')
            self.assertEqual(
                Decimal(rv.data.decode('utf-8')),
                Decimal('10') * guest_pl_margin)

            rv = c.get('/en/product/product-2')
            self.assertEqual(
                Decimal(rv.data.decode('utf-8')),
                Decimal('15') * guest_pl_margin)

    @with_transaction()
    def test_0020_test_party_price(self):
        """
        Test the pricelist lookup algorithm when a price is defined on party
        """
        pool = Pool()
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        party_pl_margin = Decimal('1.10')

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

            rv = c.get('/en/product/product-1')
            self.assertEqual(
                Decimal(rv.data.decode('utf-8')),
                Decimal('10') * party_pl_margin)
            rv = c.get('/en/product/product-2')
            self.assertEqual(
                Decimal(rv.data.decode('utf-8')),
                Decimal('15') * party_pl_margin)

    @with_transaction()
    def test_0030_test_guest_price_fallback(self):
        """
        Test the pricelist lookup algorithm if it falls back to guest pricing
        if a price is NOT specified for a party.
        """
        pool = Pool()
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        guest_pl_margin = Decimal('1.20')

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    }
                )
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.get('/en/product/product-1')
            self.assertEqual(
                Decimal(rv.data.decode('utf-8')),
                Decimal('10') * guest_pl_margin)
            rv = c.get('/en/product/product-2')
            self.assertEqual(
                Decimal(rv.data.decode('utf-8')),
                Decimal('15') * guest_pl_margin)

    @with_transaction()
    def test_0040_availability(self):
        """
        Test the availability returned for the products
        """
        pool = Pool()
        Company = pool.get('company.company')
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

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        product1 = template1.products[0]

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/product-availability/product-1')
            availability = json.loads(rv.data)
            self.assertEqual(availability['quantity'], 0.00)
            self.assertEqual(availability['forecast_quantity'], 0.00)

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
            'planned_date': datetime.date.today(),
            'effective_date': datetime.date.today(),
            'state': 'draft',
        }])
        stock2, = StockMove.create([{
            'product': product1.id,
            'unit': template1.sale_uom.id,
            'quantity': 10,
            'from_location': supplier,
            'to_location': website.stock_location.id,
            'company': website.company.id,
            'unit_price': Decimal('1'),
            'cost_price': Decimal('1'),
            'currency': website.currencies[0].id,
            'planned_date': datetime.date.today() + relativedelta(days=1),
            'effective_date': datetime.date.today() + relativedelta(days=1),
            'state': 'draft'
        }])
        StockMove.write([stock1], {
            'state': 'done'
        })

        locations = Location.search([('type', '=', 'storage')])

        with app.test_client() as c:
            with Transaction().set_context(
                    {'locations': list(map(int, locations))}):
                rv = c.get('/en/product-availability/product-1')
                availability = json.loads(rv.data)
                self.assertEqual(availability['forecast_quantity'], 20.00)
                self.assertEqual(availability['quantity'], 10.00)

    @with_transaction()
    def test_0050_product_serialize(self):
        """
        Test the serialize() method.
        """
        pool = Pool()
        Company = pool.get('company.company')
        Uom = pool.get('product.uom')
        Media = pool.get('product.media')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)

        file_memoryview = memoryview(b'test')
        file1 = create_static_file(file_memoryview, name='test.png')
        file_memoryview = memoryview(b'test-again')
        file2 = create_static_file(file_memoryview, name='test-again.png')

        with Transaction().set_context(company=company.id):
            template, = create_product_template(
                'product-1',
                [{
                    'type': 'goods',
                    'salable': True,
                    'list_price': Decimal('10'),
                }],
                uri='product-1',
            )
            product = template.products[0]

            product_media1 = Media(**{
                'static_file': file1.id,
                'product': product.id,
            })
            product_media1.save()
            template.media = [product_media1]
            template.save()

            product_media2 = Media(**{
                'static_file': file2.id,
                'product': product.id,
            })
            product_media2.save()

            qty = 7

            app = self.get_app()
            # Without login
            with app.test_client() as c:
                c.post(
                    '/en/cart/add',
                    data={
                        'product': product.id,
                        'quantity': qty,
                    }
                )
                rv = c.get('/en/cart.json')
                data = json.loads(rv.data)

                lines = data['cart']['lines']

                self.assertEqual(lines[0]['product']['id'], product.id)
                self.assertTrue(lines[0]['product']['image'] is not None)
                self.assertEqual(
                    lines[0]['display_name'], product.name
                )

            # With login
            with app.test_client() as c:
                response = c.post(
                    '/en/login',
                    data={
                        'email': 'info@m9s.biz',
                        'password': 'password',
                        }
                    )
                self.assertEqual(response.status_code, 302)  # Login success
                c.post(
                    '/en/cart/add',
                    data={
                        'product': product.id,
                        'quantity': qty,
                    }
                )
                rv = c.get('/en/cart.json')
                data = json.loads(rv.data)

                lines = data['cart']['lines']

                self.assertEqual(lines[0]['product']['id'], product.id)
                self.assertTrue(lines[0]['product']['image'] is not None)
                self.assertEqual(
                    lines[0]['url'],
                    product.get_absolute_url(_external=True)
                )
                self.assertEqual(
                    lines[0]['display_name'], product.name
                )

    @with_transaction()
    def test_0060_warehouse_quantity(self):
        """
        Test that the sale of a product is affected by availability
        and warehouse quantity.
        """
        pool = Pool()
        Company = pool.get('company.company')
        StockMove = pool.get('stock.move')
        Location = pool.get('stock.location')
        SaleLine = pool.get('sale.line')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        product1 = template1.products[0]

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/product-availability/product-1')
            availability = json.loads(rv.data)
            self.assertEqual(availability['quantity'], 0.00)
            self.assertEqual(availability['forecast_quantity'], 0.00)

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
            'planned_date': datetime.date.today(),
            'effective_date': datetime.date.today(),
            'state': 'draft',
        }])
        StockMove.write([stock1], {
            'state': 'done'
        })

        headers = Headers([('Referer', '/')])

        self.assertEqual(product1.is_backorder, True)

        # Set product warehouse quantity
        product1.min_warehouse_quantity = 11
        product1.save()

        self.assertEqual(product1.is_backorder, False)

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

            rv = c.post(
                '/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 5
                },
                headers=headers
            )
            # Cannot add to cart, available quantity < warehouse quantity
            self.assertTrue(rv.location.endswith('/'))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(SaleLine.search([], count=True), 0)

        # Try a service product
        product1.template.type = 'service'
        product1.template.save()

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

            rv = c.post(
                '/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 5
                },
            )
            # Add to cart proceeds normally
            self.assertTrue(rv.location.endswith('/cart'))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(SaleLine.search([], count=True), 1)

    @with_transaction()
    def test_0100_cart_wo_login(self):
        """
        Check if cart works without login

         * Add 5 units of item to cart
         * Check that the number of orders in system is 1
         * Check if the lines is 1 for that order
        """
        pool = Pool()
        Company = pool.get('company.company')
        Sale = pool.get('sale.sale')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

        product1 = template1.products[0]
        quantity = 5

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                }
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

        sales = Sale.search([])
        self.assertEqual(len(sales), 1)
        sale = sales[0]
        self.assertEqual(len(sale.lines), 1)
        self.assertEqual(sale.lines[0].product, product1)
        self.assertEqual(sale.lines[0].quantity, quantity)

    @with_transaction()
    def test_0110_cart_diff_apps(self):
        """
        Call the cart with two different applications
        and assert they are different but same empty carts
        """
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_client() as c1:
            rv1 = c1.get('/en/cart')
            self.assertEqual(rv1.status_code, 200)
            data1 = rv1.data

        with app.test_client() as c2:
            rv2 = c2.get('/en/cart')
            self.assertEqual(rv2.status_code, 200)
            data2 = rv2.data

        # Both are empty active records
        self.assertTrue(
            data1.decode('utf-8') == data2.decode('utf-8') == 'Cart:None,0,')

    @with_transaction()
    def test_0115_cart_diff_apps2(self):
        """
        Call the cart with two different applications
        and assert they are not equal. They become different
        with the cart number added.
        """
        pool = Pool()
        Company = pool.get('company.company')
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c1:
            c1.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 5
                }
            )
            rv1 = c1.get('/en/cart')
            self.assertEqual(rv1.status_code, 200)
            data1 = rv1.data

        with Transaction().set_context(company=company.id), \
            app.test_client() as c2:
            c2.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 5
                }
            )
            rv2 = c2.get('/en/cart')
            self.assertEqual(rv2.status_code, 200)
            data2 = rv2.data

        self.assertTrue(data1.decode('utf-8') != data2.decode('utf-8'))

    @with_transaction()
    def test_0130_add_items_after_login(self):
        """
        An user browses a cart, adds items and logs in
        Expected behaviour :  The items in the guest cart are added to the
        registered cart of the user upon login
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            c.post(
                '/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 5
                }
            )
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            cart_data1 = rv.data.decode('utf-8')[6:]

            # Login now and access cart
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
            cart_data2 = rv.data.decode('utf-8')[6:]

            self.assertEqual(cart_data1, cart_data2)

    @with_transaction()
    def test_0135_add_to_cart(self):
        """
        Test the add and set modes of add_to_cart
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

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
            c.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 7
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,7,70.00')

            c.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 7
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,7,70.00')

            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 7, 'action': 'add'
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,14,140.00')

    @with_transaction()
    def test_0140_cart_after_logout(self):
        """
        When the user logs out his guest cart will always be empty

        * Login
        * Add a product to cart
        * Logout
        * Check the cart, should have 0 quantity and different cart id
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

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

            c.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 7
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,7,70.00')

            response = c.get('/en/logout')
            self.assertEqual(response.status_code, 302)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:None,0,')

    @with_transaction()
    def test_0150_same_user_two_sessions(self):
        """
        A registered user should see the same cart on two different sessions
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            rv = c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 6
                    })
            self.assertEqual(rv.status_code, 302)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,6,60.00')

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post('/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,6,60.00')

    @with_transaction()
    def test_0160_delete_line(self):
        """
        Try deleting a line from the cart
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Cart = pool.get('nereid.cart')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        product1 = template1.products[0]
        product2 = template2.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # Add 6 of first product
            rv = c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 6
                    })
            self.assertEqual(rv.status_code, 302)

            # Add 10 of next product
            rv = c.post('/en/cart/add',
                data={
                    'product': product2.id,
                    'quantity': 10
                })
            self.assertEqual(rv.status_code, 302)

            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,16,210.00')

            # Find the line with product1 and delete it
            cart = Cart(1)
            for line in cart.sale.lines:
                if line.product.id == product1.id:
                    break
            else:
                raise("Order line not found")

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post('/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success
            c.post('/en/cart/delete/%d' % line.id)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,10,150.00')

            # Test that ValueError is not raised if the user tries to delete
            # an already removed item
            c.post('/en/cart/delete/%d' % line.id)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,10,150.00')

    @with_transaction()
    def test_0170_clear_cart(self):
        """
        Clear the cart completely
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Cart = pool.get('nereid.cart')
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        product1 = template1.products[0]
        product2 = template2.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # Add 6 of first product
            rv = c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 6
                })
            self.assertEqual(rv.status_code, 302)

        cart = Cart(1)
        sale = cart.sale.id

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success
            c.post('/en/cart/clear')
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:None,0,')

        self.assertFalse(Sale.search([('id', '=', sale)]))

    @with_transaction()
    def test_0180_reject_negative_quantity(self):
        """
        If a negative quantity is sent to add to cart, then reject it
        """
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
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
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        product1 = template1.products[0]
        product2 = template2.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'mail@m9s.biz',
                    'password': 'password2',
                    })
            self.assertEqual(response.status_code, 302)  # Login success
            rv = c.post('/en/cart/add',
                data={
                    'product': product2.id,
                    'quantity': 10
                    })
            self.assertEqual(rv.status_code, 302)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,10,150.00')

            # Add a negative quantity and nothing should change
            rv = c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': -10
                    })
            self.assertEqual(rv.status_code, 302)
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,10,150.00')

    @with_transaction()
    def test_0190_create_sale_order(self):
        """
        Create a sale order and it should work
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        NereidUser = pool.get('nereid.user')
        Company = pool.get('company.company')
        Currency = pool.get('currency.currency')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])
        usd, = Currency.search([
                ('code', '=', 'usd'),
                ])
        registered_user, = NereidUser.search([
                ('name', '=', 'Registered User'),
                ])

        sale, = Sale.create([{
            'party': registered_user.party.id,
            'company': company.id,
            'currency': usd.id,
        }])
        self.assertEqual(sale.party, registered_user.party)

    @with_transaction()
    def test_0200_create_draft_sale(self):
        """
        Create draft sale method
        """
        pool = Pool()
        Cart = pool.get('nereid.cart')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_request_context('/'):
            # Guest cart
            cart, = Cart.create([{
                'user': None,
                'sessionid': session.sid,
            }])
            cart.create_draft_sale()

            self.assertEqual(
                cart.sale.party, current_website.guest_user.party)
            self.assertEqual(
                cart.sale.nereid_user, current_website.guest_user)

    @with_transaction()
    def test_0210_cart_cache_header(self):
        """
        Ensure that the cart page has a no cache header
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
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.headers['Cache-Control'], 'max-age=0')

    @with_transaction()
    def test_0220_add_non_salable_product_to_cart(self):
        """
        Try to add a non-salable product to cart.
        """
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': False,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        # product1 is non-salable
        self.assertTrue(product1.salable == False)

        app = self.get_app()
        with app.test_client() as c:
            # Login now
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # You are adding a non salable product to cart
            rv = c.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 7
                    })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,0,0')

            rv = c.get('/en/')
            self.assertTrue(
                'This product is not for sale' in rv.data.decode('utf-8'))

    @with_transaction()
    def test_0230_cart_sale_taxes(self):
        """
        Test taxes and sale.refresh_taxes
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        Tax = pool.get('account.tax')
        Company = pool.get('company.company')
        Account = pool.get('account.account')
        PriceList = pool.get('product.price_list')
        ProductCategory = pool.get('product.category')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        company, = Company.search([])
        tax_account, = Account.search([
                ('name', '=', 'Main Tax'),
                ])
        sale_tax, = Tax.create([{
            'name': 'Sales Tax',
            'description': 'Sales Tax',
            'type': 'percentage',
            'rate': Decimal('0.05'),  # Rate 5%
            'company': company.id,
            'invoice_account': tax_account,
            'credit_note_account': tax_account,
            }])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        with Transaction().set_context(company=company.id):
            category = ProductCategory(template1.account_category.id)
            category.customer_taxes = [sale_tax.id]
            category.save()

            product1 = template1.products[0]
            self.assertEqual(sale_tax, product1.customer_taxes_used[0])

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            # Login now
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            c.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 7
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            # 70 (10 x 7) + 3.5 (5% Tax) = 73.50
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,7,73.50')

            c.post('/en/cart/add',
                data={
                    'product': product1.id, 'quantity': 7
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            # 70 (10 x 7) + 3.5 (5% Tax) = 73.50
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,7,73.50')

            sale, = Sale.search([])
            sale.refresh_taxes()  # Refresh Taxes
            self.assertEqual(sale.tax_amount, Decimal('3.50'))

    @with_transaction()
    def test_0240_price_change_on_quantity(self):
        """
        Test the add and set modes of add_to_cart
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        PriceList = pool.get('product.price_list')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        product1 = template1.products[0]

        # Reset the pricelists for strict comparing
        price_lists = PriceList.search([])
        for price_list in price_lists:
            for line in price_list.lines:
                line.formula = 'unit_price * 1'
                line.save()

        # Create a special price_list
        price_list, = PriceList.create([{
            'name': 'Crazy Pricelist',
            'company': company.id,
            'price': 'list_price',
            'lines': [
                ('create', [{
                    'product': product1.id,
                    'quantity': 2,
                    'formula': 'unit_price - 1',
                }])
            ],
        }])
        self.assertTrue(price_list)
        self.assertEqual(price_list.price, 'list_price')

        app = self.get_app()
        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            # Login now
            response = c.post('/en/login',
                data={
                    'email': 'info@m9s.biz',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 1
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8'), 'Cart:1,1,10.00')

            sale = Sale.search([])
            self.assertEqual(len(sale), 1)
            sale[0].price_list = price_list
            sale[0].save()

            self.templates.update({
                'shopping-cart.jinja':
                    'Cart:{{ cart.id }},{{get_cart_size()|round|int}},'
                    '{{cart.sale.total_amount}},{{get_flashed_messages()}}',
                })
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 1,
                    'action': 'add'
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            # Cart total must be 18 and not 20 due to price list
            self.assertTrue('Cart:1,2,18.00' in rv.data.decode('utf-8'))
            self.assertTrue('dropped from' in rv.data.decode('utf-8'))

            # Set quantity back to 1
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': 1, 'action': 'set'
                })
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)
            # Cart total must be 10 due to price list
            self.assertTrue('Cart:1,1,10.00' in rv.data.decode('utf-8'))
            self.assertTrue('increased from' in rv.data.decode('utf-8'))


del NereidModuleTestCase



