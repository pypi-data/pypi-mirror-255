# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import json

from decimal import Decimal

from lxml import objectify

from trytond.exceptions import UserError
from trytond.modules.company.tests import set_company
from trytond.modules.nereid_base.tests.common import (
    create_static_file, create_website)
from trytond.pool import Pool
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

from nereid import render_template
from nereid.testing import NereidModuleTestCase


def create_product_category(name):
    """
    Creates a product category

    :param name: Name of the product category
    """
    pool = Pool()
    Category = pool.get('product.category')

    return Category.create([{'name': name}])


def create_product_template(name, vlist, uri, uom='Unit',
        displayed_on_eshop=True, cost_price=None):
    """
    Create a product template with products and return its ID

    :param name: Name of the product
    :param vlist: List of dictionaries of values to create
    :param uri: uri of product template
    :param uom: Note it is the name of UOM (not symbol or code)
    :param displayed_on_eshop: Boolean field to display product
                               on shop or not
    """
    pool = Pool()
    ProductTemplate = pool.get('product.template')
    Uom = pool.get('product.uom')

    for values in vlist:
        values['name'] = name
        values['default_uom'], = Uom.search([('name', '=', uom)], limit=1)
        values['products'] = [
            ('create', [{
                'uri': uri,
                'displayed_on_eshop': displayed_on_eshop,
                'cost_price': cost_price,
            }])
        ]

    return ProductTemplate.create(vlist)


def create_test_products():
    # Create product templates with products
    pool = Pool()
    Company = pool.get('company.company')

    company, = Company.search([])
    with set_company(company), Transaction().set_context(company=company.id):
        category, = create_product_category('Category')
        category2, = create_product_category('Category 2')
        category3, = create_product_category('Category 3')
        create_product_template(
            'product 1',
            [{
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
            }],
            uri='product-1',
            cost_price=Decimal('5'),
        )
        create_product_template(
            'product 2',
            [{
                'categories': [('add', [category2.id])],
                'type': 'goods',
                'list_price': Decimal('20'),
            }],
            uri='product-2',
            cost_price=Decimal('5'),
        )
        create_product_template(
            'product 3',
            [{
                'categories': [('add', [category3.id])],
                'type': 'goods',
                'list_price': Decimal('30'),
            }],
            uri='product-3',
            cost_price=Decimal('5'),
        )
        create_product_template(
            'product 4',
            [{
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('30'),
            }],
            uri='product-4',
            cost_price=Decimal('5'),
            displayed_on_eshop=False
        )


class NereidCatalogTestCase(NereidModuleTestCase):
    'Test Nereid Catalog module'
    module = 'nereid_catalog'

    def setUp(self):
        self.templates = {
            'home.jinja':
                '''
                {{current_website.get_currencies()}}
                {% for image in product.images %}
                {{ image.name }}
                {% endfor %}
                ''',
            'login.jinja':
                '{{ login_form.errors }} {{get_flashed_messages()}}',
            'product-list.jinja':
                '{% for product in products %}'
                '|{{ product.name }}|{% endfor %}',
            'category.jinja':
                '{% for product in products %}'
                '|{{ product.name }}|{% endfor %}',
            'category-list.jinja':
                '{%- for category in categories %}'
                '|{{ category.name }}|'
                '{%- endfor %}',
            'search-results.jinja':
                '{% for product in products %}'
                '|{{ product.name }}|{% endfor %}',
            'product.jinja': '{{ product.sale_price(product.id) }}',
            }

    @with_transaction()
    def test_0010_get_price(self):
        """
        The price returned must be the list price of the product, no matter
        the quantity
        """
        pool = Pool()
        Company = pool.get('company.company')

        create_website()
        create_test_products()
        app = self.get_app()

        company, = Company.search([])

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
                rv = c.get('/en/product/product-1')
                self.assertEqual(rv.data.decode('utf-8'), '10')

    @with_transaction()
    def test_0020_list_view(self):
        """
        Call the render list method to get list of all products
        """
        create_website()
        create_test_products()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/en/products')
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 1||product 2||product 3|')

    @with_transaction()
    def test_0030_quick_search(self):
        """
        Check if quick search works
        """
        create_website()
        create_test_products()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/en/search?q=product')
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 1||product 2||product 3|')

    @with_transaction()
    def test_0040_product_sitemap_index(self):
        """
        Assert that the sitemap index returns 1 result
        """
        create_website()
        create_test_products()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/en/sitemaps/product-index.xml')
            xml = objectify.fromstring(rv.data)
            self.assertTrue(xml.tag.endswith('sitemapindex'))
            self.assertEqual(len(xml.getchildren()), 1)
            self.assertEqual(xml.sitemap.loc.pyval.split('localhost', 1)[-1],
                '/en/sitemaps/product-1.xml?priority=0.5')

            rv = c.get('/en/sitemaps/product-1.xml')
            xml = objectify.fromstring(rv.data)
            self.assertTrue(xml.tag.endswith('urlset'))
            self.assertEqual(len(xml.getchildren()), 3)

    @with_transaction()
    def test_0060_get_recent_products(self):
        """
        Get the recent products list
        """
        create_website()
        create_test_products()
        app = self.get_app(
            CACHE_TYPE='cachelib.SimpleCache'
        )
        pool = Pool()
        Company = pool.get('company.company')

        company, = Company.search([])
        with set_company(company), \
            Transaction().set_context(company=company.id), \
            app.test_client() as c:
            rv = c.get('/en/products/+recent')
            self.assertEqual(
                json.loads(rv.data.decode('utf-8'))['products'], [])

            rv = c.get('/en/product/product-1')
            rv = c.get('/en/products/+recent')
            self.assertEqual(
                len(json.loads(rv.data.decode('utf-8'))['products']), 1)

            rv = c.post('/en/products/+recent', data={'product_id': 2})
            self.assertEqual(
                len(json.loads(rv.data.decode('utf-8'))['products']), 2)
            rv = c.get('/en/products/+recent')
            self.assertEqual(
                len(json.loads(rv.data.decode('utf-8'))['products']), 2)

    @with_transaction()
    def test_0070_displayed_on_eshop(self):
        """
        Ensure only displayed_on_eshop products are displayed on the site
        """
        create_website()
        create_test_products()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/en/product/product-4')
            self.assertEqual(rv.status_code, 404)

    @with_transaction()
    def test_0080_render_product_by_category(self):
        """
        Render product using user friendly paths.
        """
        create_website()
        create_test_products()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/en/product/category/sub-category/product-1')
            self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0090_products_displayed_on_eshop(self):
        """
        Test for the products_displayed_on_eshop function fields
        """
        pool = Pool()
        ProductTemplate = pool.get('product.template')
        Uom = pool.get('product.uom')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        unit, = Uom.search([('name', '=', 'Unit')])

        with Transaction().set_context(company=company.id):
            # Create templates with 2 displayed on eshop and 1 not
            template1, = ProductTemplate.create([{
                'name': 'Product Template 1',
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': unit,
                'products': [('create', [
                                    {
                                        'uri': 'product-1-variant-1',
                                        'displayed_on_eshop': True,
                                        'cost_price': Decimal('5'),
                                    }, {
                                        'uri': 'product-1-variant-2',
                                        'displayed_on_eshop': True,
                                        'cost_price': Decimal('5'),
                                    }, {
                                        'uri': 'product-1-variant-3',
                                        'displayed_on_eshop': False,
                                        'cost_price': Decimal('5'),
                                    },
                                    ])
                            ]
                        }])

        self.assertEqual(len(template1.products_displayed_on_eshop), 2)
        self.assertEqual(len(template1.products), 3)

    @with_transaction()
    def test_0100_product_images(self):
        """
        Test for adding product images
        """
        pool = Pool()
        Product = pool.get('product.product')
        Media = pool.get('product.media')

        create_website()
        file_memoryview = memoryview(b'test-content')
        static_file = create_static_file(file_memoryview, name='logo.png')
        create_test_products()
        product, = Product.search([], limit=1)

        Media.create([{
                    'product': product.id,
                    'template': product.template.id,
                    'static_file': static_file.id,
                    }])

        app = self.get_app()
        with app.test_request_context('/'):
            home_template = render_template('home.jinja', product=product)
            self.assertTrue(static_file.name in home_template)

    @with_transaction()
    def test_0210search_domain_conversion(self):
        '''
        Test the search domain conversion
        '''
        pool = Pool()
        Company = pool.get('company.company')

        create_website()
        create_test_products()
        app = self.get_app()

        company, = Company.search([])

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            # Render all products
            rv = c.get('/en/products')
            self.assertEqual(len(rv.data.decode('utf-8').split('||')), 3)
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 1||product 2||product 3|')

            # Render product with uri
            rv = c.get('/en/product/product-1')
            self.assertEqual(rv.data.decode('utf-8'), '10')

            rv = c.get('/en/product/product-2')
            self.assertEqual(rv.data.decode('utf-8'), '20')

    @with_transaction()
    def test_0220_inactive_template(self):
        '''
        Assert that inactive variants and the variants of inactive products
        are not displayed
        '''
        pool = Pool()
        Product = pool.get('product.product')
        Company = pool.get('company.company')

        create_website()
        create_test_products()
        app = self.get_app()

        company, = Company.search([])

        product1, = Product.search([
                ('uri', '=', 'product-1'),
                ])

        with Transaction().set_context(company=company.id), \
            app.test_client() as c:
            # Render all products
            rv = c.get('/en/products')
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 1||product 2||product 3|')

            product1.active = False
            product1.save()
            self.assertEqual(product1.template.active, 1)
            rv = c.get('/en/products')
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 2||product 3|')

            template1 = product1.template
            template1.active = False
            template1.save()
            rv = c.get('/en/products')
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 2||product 3|')

            rv = c.get('/en/products')
            self.assertEqual(rv.data.decode('utf-8'),
                '|product 2||product 3|')

            # Render product with uri
            rv = c.get('/en/product/product-1')
            self.assertEqual(rv.status_code, 404)

            rv = c.get('/en/product/product-2')
            self.assertEqual(rv.data.decode('utf-8'), '20')

    @with_transaction()
    def test_0230_get_variant_description(self):
        """
        Test to get variant description.
        If use_template_description is false, show description
        of variant else show description of product template
        """
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')

        create_website()
        create_test_products()

        product1, = Product.search([
                ('uri', '=', 'product-1'),
                ])
        template1 = Template(product1.template.id)
        template1.description = 'Description of template'
        template1.save()

        # setting use_template_description to false
        # and adding variant description
        Product.write([product1], {
            'use_template_description': False,
            'description': 'Description of product',
            })

        self.assertEqual(product1.get_description(),
            'Description of product')

        # setting use_template_description to true
        # description of variant should come from product template
        Product.write([product1], {
            'use_template_description': True,
            })

        self.assertEqual(product1.get_description(),
            'Description of template')

    @with_transaction()
    def test_0231_get_variant_long_description(self):
        """
        Test to get variant long description.
        If use_template_description is false, show description
        of variant else show description of product template
        """
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')

        create_website()
        create_test_products()

        product1, = Product.search([
                ('uri', '=', 'product-1'),
                ])
        template1 = Template(product1.template.id)
        template1.long_description = 'Long description of template'
        template1.save()

        # setting use_template_description to false
        # and adding variant long_description
        Product.write([product1], {
            'use_template_description': False,
            'long_description': 'Long description of product',
            })

        self.assertEqual(product1.get_long_description(),
            'Long description of product')

        # setting use_template_description to true
        # long_description of variant should come from product template
        Product.write([product1], {
            'use_template_description': True,
            })

        self.assertEqual(product1.get_long_description(),
            'Long description of template')

    @with_transaction()
    def test_0235_get_variant_images(self):
        """
        Test to get variant images.
        """
        pool = Pool()
        Product = pool.get('product.product')
        Media = pool.get('product.media')

        create_website()
        file_memoryview = memoryview(b'test-content1')
        static_file1 = create_static_file(file_memoryview, name='logo1.png')
        file_memoryview = memoryview(b'test-content2')
        static_file2 = create_static_file(file_memoryview, name='logo2.png')

        create_test_products()
        product, = Product.search([], limit=1)

        Media.create([{
                    'template': product.template.id,
                    'static_file': static_file1.id,
                    }])

        # There are no images for product so, it should return images
        # from template
        self.assertEqual(product.get_images()[0].id,
            static_file1.id)

        Product.write([product], {'media': [('create', [{
                'static_file': static_file2.id,
                }])]
                })
        # As the product now has images, this image should be returned
        self.assertEqual(product.get_images()[0].id, static_file2.id)

    @with_transaction()
    def test_0240_test_uri_uniqueness(self):
        """
        Test that URIs are unique for products
        """
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Uom = pool.get('product.uom')
        Company = pool.get('company.company')

        create_website()
        create_test_products()
        company, = Company.search([])

        # Create new variants with the same URI
        # Assert if UserError is raised
        product2, = Product.search([
                ('uri', '=', 'product-2'),
                ])
        with self.assertRaises(UserError):
            product2.uri = 'product-1'
            product2.save()
        with self.assertRaises(UserError):
            product2.uri = 'ProduCt-1'
            product2.save()

        # Check if we are not checking URI uniqueness if
        # new product is marked as not displayed on eshop
        product4, = Product.create([{
                'template': product2.template.id,
                'uri': 'Product-1',
                }])
        self.assertTrue(product4)

        # Check if we are checking URI uniqueness if
        # new product is marked as displayed on eshop
        with self.assertRaises(UserError):
            product5, = Product.create([{
                'template': product2.template.id,
                'uri': 'ProduCt-1',
                'displayed_on_eshop': True,
            }])

        # Check if we are not checking URI uniqueness if
        # an existing product is not marked as displayed on eshop
        product2.uri = 'product-1'
        product2.displayed_on_eshop = False
        product2.save()

        # Check if there is still only one product with displayed on eshop
        # in the database
        products = Product.search([
                ('displayed_on_eshop', '=', True),
                ('uri', '=', 'product-1'),
                ])
        self.assertTrue(len(products), 1)

        # Check if there are now in total 4 products with this uri
        # in the database
        products = Product.search([
                ('displayed_on_eshop', '=', False),
                ('uri', '=', 'product-1'),
                ])
        self.assertTrue(len(products), 4)

        # Check if we are checking URI uniqueness if
        # an existing product is marked as displayed on eshop
        with self.assertRaises(UserError):
            product2.uri = 'product-1'
            product2.displayed_on_eshop = True
            product2.save()

        # Create a new template
        category, = create_product_category('Category4')
        uom, = Uom.search([], limit=1)
        with Transaction().set_context(company=company.id):
            product_template_1, = Template.create([{
                        'name': 'Test Template',
                        'categories': [('add', [category.id])],
                        'type': 'goods',
                        'list_price': Decimal('10'),
                        'default_uom': uom.id,
                        'description': 'Template Description',
                        }])
        self.assertTrue(product_template_1)

        # Check if we are checking URI uniqueness if
        # new products are marked as displayed on eshop
        with self.assertRaises(UserError):
            Template.write([product_template_1], {
                    'products': [('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True
                    }, {
                        'uri': 'Product-1',
                        'displayed_on_eshop': True
                    }])]
                    })

    @with_transaction()
    def test_0250_test_rec_name_sorting(self):
        """
        Test if rec_name field is sorted
        """
        pool = Pool()
        ProductCategory = pool.get('product.category')

        create_website()

        product_category2, = ProductCategory.create([{
                    'name': 'Personel',
                    }])

        product_category1, = ProductCategory.create([{
                    'name': 'Automobile',
                    }])

        product_category3, = ProductCategory.create([{
                    'name': 'Household',
                    }])

        product_category4, = ProductCategory.create([{
                    'name': 'Cars',
                    'parent': product_category1.id
                    }])

        product_category5, = ProductCategory.create([{
                    'name': 'Watches',
                    }])

        # With sorting
        categories = ProductCategory.search([], order=[('rec_name', 'ASC')])

        # Category first element is Automobile/car (child)
        self.assertEqual(categories[0], product_category4)

        # Category last element is Watches  (last created)
        self.assertEqual(categories[-1], product_category5)

        # Category Second element is Automobile (parent)
        self.assertEqual(categories[1], product_category1)

        # Own order
        categories = ProductCategory.search([])

        # Category first element is Automobile/car (child)
        self.assertEqual(categories[0], product_category1)

        # Category last element is Watches  (last created)
        self.assertEqual(categories[-1], product_category5)

        # Category Second element is Automobile (parent)
        self.assertEqual(categories[1], product_category4)

    @with_transaction()
    def test_0260_copy_product(self):
        '''
        Test product copy
        '''
        pool = Pool()
        Product = pool.get('product.product')

        create_website()
        create_test_products()

        product1, = Product.search([
                ('uri', '=', 'product-1'),
                ])
        product2, = Product.copy([product1])
        self.assertEqual(product2.uri, '%s-copy-1' % product1.uri)


del NereidModuleTestCase
