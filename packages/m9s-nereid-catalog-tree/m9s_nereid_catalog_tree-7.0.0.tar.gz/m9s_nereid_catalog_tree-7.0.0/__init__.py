# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool

from . import tree

__all__ = ['register']


def register():
    Pool.register(
        tree.Product,
        tree.Node,
        tree.ProductNodeRelationship,
        tree.Website,
        tree.WebsiteTreeNode,
        module='nereid_catalog_tree', type_='model')
