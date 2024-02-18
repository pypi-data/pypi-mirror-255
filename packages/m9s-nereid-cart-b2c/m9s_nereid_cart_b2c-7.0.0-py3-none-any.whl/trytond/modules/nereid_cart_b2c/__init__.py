# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import cart, channel, product, sale, website

__all__ = ['register']


def register():
    Pool.register(
        product.Product,
        sale.Sale,
        sale.SaleLine,
        channel.SaleChannel,
        cart.Cart,
        website.Website,
        module='nereid_cart_b2c', type_='model')
