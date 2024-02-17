# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from sql import Literal
from werkzeug.exceptions import NotFound

from trytond.exceptions import UserError
from trytond.model import (
    DeactivableMixin, ModelSQL, ModelView, fields, sequence_ordered, tree)
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

from nereid import abort, render_template, request, route, url_for
from nereid.contrib.pagination import QueryPagination
from nereid.contrib.sitemap import SitemapIndex, SitemapSection
from nereid.helpers import context_processor, slugify


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    nodes = fields.One2Many('product.product-product.tree_node',
        'product', 'Tree Nodes')

    @classmethod
    @route('/product/<uri>')
    @route('/product/<path:path>/<uri>')
    def render(cls, uri, path=None):
        """
        If node is in the url arguments, translate that into an active record
        of the node and send it in the context
        """
        rv = super(Product, cls).render(uri, path)
        Node = Pool().get('product.tree_node')

        node = request.args.get('node', type=int)
        if node and not isinstance(rv, NotFound):
            try:
                rv.context['node'] = Node(node)
            except ValueError:
                pass
        return rv


class Node(DeactivableMixin, tree(separator=' / '), sequence_ordered(),
        ModelSQL, ModelView):
    """
    Tree Node
    A tree is a hierachcial way to group products together.
    A vertex or node is the fundamental unit of which graphs/trees are formed
    """
    __name__ = "product.tree_node"

    name = fields.Char('Name', required=True, translate=True)
    slug = fields.Char('Slug', required=True, translate=True)
    type_ = fields.Selection([
            ('catalog', 'Catalog'),
            ], 'Type', required=True)
    parent = fields.Many2One('product.tree_node', 'Parent',
        domain=[('type_', '=', Eval('type_'))],
        left='left', right='right', ondelete="RESTRICT")
    children = fields.One2Many('product.tree_node', 'parent', 'Children',
        add_remove=[('id', '!=', Eval('id'))])
    left = fields.Integer('Left')
    right = fields.Integer('Right')
    products = fields.One2Many('product.product-product.tree_node', 'node',
        'Products')
    products_per_page = fields.Integer('Products per Page')
    description = fields.Text('Description', translate=True)
    image = fields.Many2One('nereid.static.file', 'Image')
    image_preview = fields.Function(fields.Binary('Image Preview'),
        'get_image_preview')
    display = fields.Selection([
            ('product.product', 'Product Variants'),
            ('product.template', 'Product Templates'),
            ('product.tree_node', 'Sub Collections'),
            ], 'Display', required=True)
    template = fields.Selection('get_template', 'Template', required=True)

    # parent for rec_name needed
    @fields.depends('name', 'slug', 'parent', '_parent_parent.id')
    def on_change_with_slug(self):
        """
        On change the name and slug, ensure that the slug field is auto
        filled with a generated slug, if the field is empty
        """
        if not self.slug and self.name:
            self.slug = slugify(self.get_rec_name('rec_name'))
        return self.slug

    @classmethod
    def get_template(cls):
        """
        Return templates available for node.
        Downstream module can add new templates
        """
        return [('catalog/node.html', 'catalog/node.html')]

    @staticmethod
    def default_left():
        return 0

    @staticmethod
    def default_right():
        return 0

    @staticmethod
    def default_products_per_page():
        return 10

    @staticmethod
    def default_template():
        return 'catalog/node.html'

    def _get_products(self):
        """
        Return a query based on the node settings. This is separated for
        easy subclassing. The returned value would be a tuple with the
        dollowing elements:

            * The Model instance
            * Select query instance
            * The Table instance for the SQL Pagination

        """
        pool = Pool()
        Node = pool.get('product.tree_node')
        Product = pool.get('product.product')
        ProductTemplate = pool.get('product.template')
        ProductNodeRelation = pool.get('product.product-product.tree_node')

        ProductTable = Product.__table__()
        TemplateTable = ProductTemplate.__table__()
        RelTable = ProductNodeRelation.__table__()
        NodeTable = Node.__table__()

        if self.display == 'product.product':
            order_by = (RelTable.sequence.asc,)
            if getattr(Product, 'variant_name', None):
                order_by += (ProductTable.variant_name.asc,)
            else:
                order_by += (TemplateTable.name.asc,)
            query = ProductTable.join(
                TemplateTable,
                condition=(TemplateTable.id == ProductTable.template)
            ).join(
                RelTable,
                condition=(RelTable.product == ProductTable.id)
            ).join(
                NodeTable,
                condition=(RelTable.node == NodeTable.id)
            ).select(
                where=(
                    TemplateTable.active &
                    ProductTable.displayed_on_eshop &
                    ProductTable.active &
                    (NodeTable.left >= Literal(self.left)) &
                    (NodeTable.right <= Literal(self.right))
                ),
                order_by=order_by
            )
            return Product, query, ProductTable

        elif self.display == 'product.template':
            order_by = (RelTable.sequence.asc, TemplateTable.name.asc)
            query = TemplateTable.join(
                ProductTable,
                condition=(TemplateTable.id == ProductTable.template)
            ).join(
                RelTable,
                condition=(RelTable.product == ProductTable.id)
            ).join(
                NodeTable,
                condition=(RelTable.node == NodeTable.id)
            ).select(
                where=(
                    TemplateTable.active &
                    ProductTable.displayed_on_eshop &
                    ProductTable.active &
                    (NodeTable.left >= Literal(self.left)) &
                    (NodeTable.right <= Literal(self.right))
                ),
                order_by=order_by
            )
            return ProductTemplate, query, TemplateTable

    def get_products(self, page=1, per_page=None):
        """
        Return a pagination object of active records of products in the tree
        and all of its branches.

        A pagination object is returned so that the user can implement
        interfaces like infinite scroll which will need advance information of
        the number of pages that will exist.

        It is recommended to use this method instead of directly reading from
        the products (many2many) field for scalability. In addition, if a
        product is made inactive or not displayed on eshop, it will be
        overlooked by the many2many field.

        Example usage::

            {% for product in node.get_products() %}
            <li>{{ product.name }}</li>
            {% endfor %}

        :param page: The page for which the products have to be displayed
        :param per_page: The number of products to be returned in each page
        """
        if per_page is None:
            per_page = self.products_per_page

        return QueryPagination(*self._get_products(), page=page,
            per_page=per_page)

    @route('/nodes/<int:active_id>/<slug>/<int:page>')
    @route('/nodes/<int:active_id>/<slug>')
    def render(self, slug=None, page=1):
        """
        Renders a page of products in the tree and all of its branches

        :param slug: slug of the browse node to be shown
        :param page: page of the products to be displayed
        """
        if not self.slug or not self.active:
            abort(404)

        if self.type_ != 'catalog':
            # Display only catalog nodes
            abort(403)

        products = self.get_products(page=page,
            per_page=self.products_per_page)

        return render_template(self.template, products=products, node=self)

    def get_image_preview(self, name=None):
        if self.image:
            return self.image.file_binary
        return None

    @staticmethod
    def default_type_():
        return 'catalog'

    @staticmethod
    def default_display():
        return 'product.product'

    @classmethod
    @context_processor('make_tree_crumbs')
    def make_tree_crumbs(cls, node, add_home=True):
        """
        Make breadcrumb for tree node.
        """
        leaf = cls(int(node))
        crumbs = []
        while leaf:
            crumbs.append((url_for(
                        'product.tree_node.render', active_id=leaf.id,
                        slug=leaf.slug), leaf.name))
            leaf = leaf.parent
        if add_home:
            crumbs.append((url_for('nereid.website.home'), 'Home'))
        crumbs.reverse()
        return crumbs

    @classmethod
    @route('/sitemaps/tree-index.xml')
    def sitemap_index(cls):
        index = SitemapIndex(cls, [
                ('active', '=', True),
                ])
        return index.render()

    @classmethod
    @route('/sitemaps/tree-<int:page>.xml')
    def sitemap(cls, page):
        sitemap_section = SitemapSection(cls, [
                ('active', '=', True),
                ], page)
        sitemap_section.changefreq = 'daily'
        return sitemap_section.render()

    def get_absolute_url(self, **kwargs):
        return url_for('product.tree_node.render', active_id=self.id,
            slug=self.slug, **kwargs)


class ProductNodeRelationship(sequence_ordered(), ModelSQL, ModelView):
    """
    This is the relation between a node in a tree
    and a product
    """
    __name__ = 'product.product-product.tree_node'

    product = fields.Many2One('product.product', 'Product',
        ondelete='CASCADE', required=True)
    node = fields.Many2One('product.tree_node', 'Node',
        domain=[('type_', '=', 'catalog')], ondelete='CASCADE',
        required=True)

    @staticmethod
    def default_sequence():
        return 100

    @classmethod
    def __setup__(cls):
        super(ProductNodeRelationship, cls).__setup__()
        pass
        # TODO: Add unique constraint for product, node


class Website(metaclass=PoolMeta):
    __name__ = 'nereid.website'

    featured_products_node = fields.Many2One(
        'product.tree_node', 'Featured Products Node',
        domain=[('type_', '=', 'catalog')])
    latest_products_node = fields.Many2One(
        'product.tree_node', 'Latest Products Node',
        domain=[('type_', '=', 'catalog')])
    upcoming_products_node = fields.Many2One(
        'product.tree_node', 'Upcoming Products Node',
        domain=[('type_', '=', 'catalog')])


class WebsiteTreeNode(ModelSQL):
    "Website Tree Node"
    __name__ = 'nereid.website-product.tree_node'
    _table = 'website_tree_node_rel'

    website = fields.Many2One('nereid.website', 'Website',
        ondelete='CASCADE', required=True)
    node = fields.Many2One('product.tree_node', 'Tree Nodes',
        domain=[('type_', '=', 'catalog')],
        ondelete='CASCADE', required=True)
