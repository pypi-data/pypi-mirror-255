# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from itertools import chain

from lxml import objectify

from trytond.exceptions import UserError
from trytond.model.modelstorage import AccessError
from trytond.modules.nereid_base.tests.common import create_website
from trytond.modules.nereid_catalog.tests.test_module import (
    create_product_category)
from trytond.pool import Pool
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

from nereid.testing import NereidModuleTestCase


class NereidCatalogTreeTestCase(NereidModuleTestCase):
    'Test Nereid Catalog Tree module'
    module = 'nereid_catalog_tree'

    def setUp(self):
        self.templates = {
            'catalog/node.html':
            '{{ products.count }}||' +
            '{{ make_tree_crumbs(node=node)|join(", ", attribute="1") }}',
            'product.jinja': "{{ node and node.name or 'no-node' }}",
            }

    @with_transaction()
    def test_0010_create_product_node_in_tree(self):
        """
        Test if a product can be created which can be
        associated to a node
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, = Template.create([values1])

            node1, = Node.create([{
                'name': 'Node1',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

        self.assertTrue(node1)

        # Check if default tree node type is 'catalog'
        self.assertEqual(node1.type_, 'catalog')
        # Check if node1 is active by default
        self.assertTrue(node1.active)
        # Check if default display is product variant
        self.assertEqual(node1.display, 'product.product')

    @with_transaction()
    def test_0020_create_product_node_with_children(self):
        """
        Test if a product can be created to find
        its children
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            values2 = {
                'name': 'Product-2',
                'categories': [('add', [category.id])],
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-2',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, template2 = Template.create([values1, values2])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

            self.assertTrue(node1)

            node2, = Node.create([{
                'name': 'Node2',
                'type_': 'catalog',
                'slug': 'node2',
                'products': [('create', [
                    {'product': product} for product in template2.products
                ])]
            }])

            self.assertTrue(node2)

            Node.write([node2], {
                'parent': node1
            })
            self.assertEqual(node2.parent, node1)
            self.assertTrue(node2 in node1.children)
            self.assertEqual(len(node2.children), 0)

    @with_transaction()
    def test_0025_test_slugify(self):
        """
        Test if the automatic insert of slugs works
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            values2 = {
                'name': 'Product-2',
                'categories': [('add', [category.id])],
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-2',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, template2 = Template.create([values1, values2])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

            self.assertTrue(node1)

            node2, = Node.create([{
                'name': 'Node2',
                'type_': 'catalog',
                'slug': 'node2',
                'products': [('create', [
                    {'product': product} for product in template2.products
                ])]
            }])

            self.assertTrue(node2)

            Node.write([node2], {
                'parent': node1
            })

            node3 = Node(
                name='Node3 with Ümläuts &%§',
                type_='catalog',
                parent=node2,
                )
            node3.on_change_with_slug()

            self.assertEqual(node3.slug,
                'node1-node2-node3-with-umlauts')

    @with_transaction()
    def test_0030_nereid_render_method(self):
        """
        Test if the url for the active id of the current node
        returns all the children and its branches
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            values2 = {
                'name': 'Product-2',
                'categories': [('add', [category.id])],
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-2',
                        'displayed_on_eshop': True,
                    }, {
                        'uri': 'product-21',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            values3 = {
                'name': 'Product-3',
                'categories': [('add', [category.id])],
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-3',
                        'displayed_on_eshop': False
                    }, {
                        'uri': 'product-3_2',
                        'active': False,
                        'cost_price': Decimal('5'),
                        'displayed_on_eshop': True,
                    }])
                ]
            }

            template1, template2, template3, = Template.create([
                values1, values2, values3
            ])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

            self.assertTrue(node1)

            node2, = Node.create([{
                'name': 'Node2',
                'type_': 'catalog',
                'slug': 'node2',
                'display': 'product.template',
                'products': [('create', [
                    {'product': product} for product in template2.products
                ])]
            }])

            self.assertTrue(node2)

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

            self.assertTrue(node2)

            app = self.get_app()

            with app.test_client() as c:
                url = '/en/nodes/{0}/{1}/{2}'.format(
                    node1.id, node1.slug, 1)
                rv = c.get(url)
                self.assertEqual(rv.status_code, 200)
                # Test is if there are 3 products.
                # 1 from node1 and 2 from node2
                # Get the node record by searching it, because current one
                # is cached.
                node1, = Node.search([('id', '=', node1.id)])
                self.assertEqual(
                    node1.get_products(per_page=10).all_items(),
                    list(template1.products + template2.products))
                self.assertEqual(rv.data.decode('utf-8'), '3||Home, Node1')

                url = '/en/nodes/{0}/{1}/{2}'.format(node2.id, node2.slug, 1)
                rv = c.get(url)
                self.assertEqual(rv.status_code, 200)
                # Test if products length is 1 as display of
                # node2 is set to 'product.template'
                node2, = Node.search([('id', '=', node2.id)])
                self.assertEqual(Node(node2.id).get_products().all_items(),
                    [template2])
                self.assertEqual(rv.data.decode('utf-8'), '1||Home, Node1, Node2')

    @with_transaction()
    def test_0035_product_render_method(self):
        """
        Check injection of node into template context on product rendering
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')

        create_website()
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, = Template.create([values1])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

            self.assertTrue(node1)

            app = self.get_app()

            with app.test_client() as c:
                product = template1.products[0]
                url = '/en/product/%s' % product.uri

                # With no node argument
                rv = c.get('%s' % url)
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data.decode('utf-8'), 'no-node')

                # With one valid node
                rv = c.get('%s?node=%d' % (url, node1))
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data.decode('utf-8'), node1.name)

                # With one invalid node (number)
                with self.assertRaises(AccessError) as cm:
                    rv = c.get('%s?node=999999' % url)
                self.assertEqual(str(cm.exception),
                    '''You are trying to read records "999999" of "Tree Node"'''
                    ''' that don't exist. - ''')

                # With another invalid node (chars)
                rv = c.get('%s?node=sometext' % url)
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data.decode('utf-8'), 'no-node')

    @with_transaction()
    def test_0040_create_product_with_parent_as_itself(self):
        """
        This test creates a node and sets the product as
        the parent of itself, which shouldn't happen
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, = Template.create([values1])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

            self.assertTrue(node1)
            self.assertRaises(UserError, Node.write, [node1], {
                    'parent': node1
                    })

    @with_transaction()
    def test_0050_product_template_disabled(self):
        """
        Ensure that the products are not listed when the template is
        disabled
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, = Template.create([values1])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product} for product in template1.products
                ])]
            }])

            app = self.get_app()

            with app.test_client() as c:
                rv = c.get('/en/nodes/%d/_/1' % node1.id)
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data.decode('utf-8')[0], '1')

            node1, = Node.search([('id', '=', node1.id)])
            self.assertEqual(node1.get_products().count, 1)
            self.assertEqual(len(node1.products), 1)

            for product in template1.products:
                product.active = False
                product.save()
            template1.active = False
            template1.save()

        with app.test_client() as c:
            rv = c.get('/en/nodes/%d/_/1' % node1.id)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data.decode('utf-8')[0], '0')

        node1, = Node.search([('id', '=', node1.id)])
        self.assertEqual(node1.get_products().count, 0)
        self.assertEqual(len(node1.products), 1)

    @with_transaction()
    def test_0060_make_tree_crumbs(self):
        """
        Test to get breadcrumbs on node template
        """
        pool = Pool()
        Node = pool.get('product.tree_node')

        default_node, = Node.create([{
            'name': 'root',
            'slug': 'root',
        }])

        create_website()
        app = self.get_app()

        parent_node, = Node.create([{
            'name': 'Node1',
            'type_': 'catalog',
            'slug': 'node1',
            'parent': default_node,
        }])

        child_node, = Node.create([{
            'name': 'Node2',
            'type_': 'catalog',
            'slug': 'node2',
            'parent': parent_node,
        }])

        with app.test_client() as c:
            rv = c.get('/en/nodes/%d/node2' % child_node.id)
            self.assertEqual(rv.data.decode('utf-8')[3:],
                "Home, root, Node1, Node2")

    @with_transaction()
    def test_0070_tree_sitemap_index(self):
        """
        Assert that the sitemap index returns 1 result
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')
        app = self.get_app()

        with Transaction().set_context(company=company.id):
            values1 = {
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            values2 = {
                'name': 'Product-2',
                'categories': [('add', [category.id])],
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-2',
                        'displayed_on_eshop': True,
                        'cost_price': Decimal('5'),
                    }])
                ]
            }

            template1, template2 = Template.create([values1, values2])

            node1, = Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product}
                    for product in template1.products
                ])]
            }])
            self.assertTrue(node1)

            node2, = Node.create([{
                'name': 'Node2',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': product}
                    for product in template2.products
                ])]
            }])
            self.assertTrue(node2)

        with app.test_client() as c:
            # Check for 1 tiem in the sitemap index
            rv = c.get('/en/sitemaps/tree-index.xml')
            xml = objectify.fromstring(rv.data)
            self.assertTrue(xml.tag.endswith('sitemapindex'))
            self.assertEqual(len(xml.getchildren()), 1)

            # Check for 2 items in the sitemap
            rv = c.get('/en/sitemaps/tree-index.xml')
            rv = c.get(xml.sitemap.loc.pyval.split('localhost', 1)[-1])
            xml = objectify.fromstring(rv.data)
            self.assertTrue(xml.tag.endswith('urlset'))
            self.assertEqual(len(xml.getchildren()), 2)

    @with_transaction()
    def test_0090_product_sequence(self):
        """
        Ensure that the products are displayed according to the sequence
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            template1, = Template.create([{
                'name': 'Product-1',
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [
                        {
                            'uri': 'product-1',
                            'displayed_on_eshop': True,
                            'cost_price': Decimal('5'),
                        },
                        {
                            'uri': 'product-2',
                            'displayed_on_eshop': True,
                            'cost_price': Decimal('5'),
                        },
                        {
                            'uri': 'product-3',
                            'displayed_on_eshop': True,
                            'cost_price': Decimal('5'),
                        },
                        {
                            'uri': 'product-4',
                            'displayed_on_eshop': True,
                            'cost_price': Decimal('5'),
                        },
                        {
                            'uri': 'product-5',
                            'displayed_on_eshop': True,
                            'cost_price': Decimal('5'),
                        },
                    ])
                ]
            }])

            prod1, prod2, prod3, prod4, prod5 = template1.products

            node1, node2 = Node.create([{
                'name': 'Node 1',
                'type_': 'catalog',
                'slug': 'node1',
                'products': [('create', [
                    {'product': prod4, 'sequence': 10},
                    {'product': prod1, 'sequence': 20},
                ])]
            }, {
                'name': 'Node 2',
                'type_': 'catalog',
                'slug': 'node2',
                'products': [('create', [
                    {'product': prod3, 'sequence': 10},
                    {'product': prod2, 'sequence': 20},
                    {'product': prod1, 'sequence': 5},
                ])]
            }])

            self.assertTrue(node1)
            self.assertTrue(node2)

            node1, = Node.search([('id', '=', node1.id)])
            node2, = Node.search([('id', '=', node2.id)])

            self.assertEqual(list(node1.get_products().items()),
                [prod4, prod1])
            self.assertEqual(list(node2.get_products().items()),
                [prod1, prod3, prod2])

    @with_transaction()
    def test_0100_product_distinct(self):
        """
        Ensure that template pagination really works
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Node = pool.get('product.tree_node')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        category, = create_product_category('Category')

        with Transaction().set_context(company=company.id):
            templates = Template.create([{
                'name': 'Product-%s' % x,
                'categories': [('add', [category.id])],
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'products': [
                    ('create', [
                        {
                            'uri': 'product-%s-%s' % (x, v),
                            'cost_price': Decimal('5'),
                            'displayed_on_eshop': True,
                        } for v in range(0, 10)
                    ])
                ]
            } for x in range(0, 10)])

            node1, = Node.create([{
                'name': 'Node 1',
                'type_': 'catalog',
                'slug': 'node1',
                'display': 'product.product',
                'products': [
                    ('create', [
                        {'product': prod.id, 'sequence': 10}
                        for prod in chain(*[t.products for t in templates])
                    ]
                    )
                ]
            }])

            self.assertTrue(node1)

            node1, = Node.search([('id', '=', node1.id)])

            self.assertEqual(len(node1.get_products().all_items()), 100)
            self.assertEqual(node1.get_products().count, 100)
            self.assertEqual(len(list(node1.get_products().items())), 10)
            self.assertEqual(len(list(node1.get_products(page=10).items())), 10)

            node1.display = 'product.template'
            node1.save()

            self.assertEqual(len(node1.get_products().all_items()), 10)
            self.assertEqual(len(list(node1.get_products().items())), 10)


del NereidModuleTestCase
