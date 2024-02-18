# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import product, website

__all__ = ['register']


def register():
    Pool.register(
        product.Product,
        product.ProductAttribute,
        product.Template,
        website.Website,
        module='nereid_webshop_elastic_search', type_='model')
