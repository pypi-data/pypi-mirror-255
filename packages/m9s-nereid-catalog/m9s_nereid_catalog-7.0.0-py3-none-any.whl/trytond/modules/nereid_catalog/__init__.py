# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool

from . import product, website

__all__ = ['register']


def register():
    Pool.register(
        product.Product,
        product.ProductTemplate,
        product.ProductCategory,
        product.ProductMedia,
        product.ProductsRelated,
        website.WebSite,
        module='nereid_catalog', type_='model')
