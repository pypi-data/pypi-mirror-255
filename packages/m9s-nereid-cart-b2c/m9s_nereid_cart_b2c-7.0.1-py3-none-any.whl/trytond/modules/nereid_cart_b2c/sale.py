# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from functools import partial

from babel import numbers

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

from nereid import (
    abort, current_locale, current_user, flash, redirect, request, url_for)
from nereid.contrib.locale import make_lazy_gettext
from nereid.ctx import has_request_context

_ = make_lazy_gettext('nereid_cart_b2c')


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    is_cart = fields.Boolean(
        'Is Cart Order?', readonly=True
    )
    website = fields.Many2One(
        'nereid.website', 'Website', readonly=True
    )
    nereid_user = fields.Many2One(
        'nereid.user', 'Nereid User'
    )

    @staticmethod
    def default_is_cart():
        """Dont make this as a default as this would cause orders being placed
        from backend to be placed under default.
        """
        return False

    @classmethod
    def default_price_list(cls):
        '''
        Get the pricelist of the active user.
        In the event that the logged in user does not have a pricelist
        set against the party, the channel's pricelist is chosen.
        '''
        pool = Pool()
        User = pool.get('res.user')

        price_list = super().default_price_list()

        if not has_request_context():
            # Not a nereid request
            return price_list

        user = User(Transaction().user)
        channel = user.current_channel
        channel_price_list = (channel.price_list.id
            if channel and channel.price_list else None)

        # If control reaches here, then this is a nereid request. Lets try
        # and personalise the pricelist of the user logged in.
        if current_user.is_anonymous:
            # Sorry anonymous users, you get the shop price
            return channel_price_list

        if current_user.party.sale_price_list:
            # There is a sale pricelist for the specific user's party.
            return current_user.party.sale_price_list.id

        return channel_price_list

    def refresh_taxes(self):
        '''
        Reload taxes of all sale lines
        '''
        for line in self.lines:
            line.refresh_taxes()

    def find_existing_line(self, product_id):
        """Return existing sale line for given product"""
        pool = Pool()
        SaleLine = pool.get('sale.line')

        lines = SaleLine.search([
            ('sale', '=', self.id),
            ('product', '=', product_id),
        ])
        return lines[0] if lines else None

    def _add_or_update(self, product_id, quantity, action='set'):
        '''Add item as a line or if a line with item exists
        update it for the quantity

        :param product: ID of the product
        :param quantity: Quantity
        :param action: set - set the quantity to the given quantity
                       add - add quantity to existing quantity
        '''
        pool = Pool()
        SaleLine = pool.get('sale.line')
        Product = pool.get('product.product')

        order_line = self.find_existing_line(product_id)
        product = Product(product_id)

        old_price = Decimal('0.0')
        if order_line:
            old_price = order_line.unit_price
            order_line.unit = order_line.unit.id
            order_line.quantity = (quantity if action == 'set'
                else quantity + order_line.quantity)
            order_line.on_change_quantity()
        else:
            order_line = SaleLine()
            order_line.sale = self
            order_line.product = product
            order_line.quantity = quantity
            order_line.on_change_product()
        # Since version 7.0 price lists do not return a fallback value. In that
        # case we use the list price as fallback.
        # https://foss.heptapod.net/tryton/tryton/-/issues/13013
        if order_line.unit_price is None:
            order_line.unit_price = product.list_price_used

        if old_price and old_price != order_line.unit_price:
            vals = {
                'product_name': product.name,
                'currency': self.currency.code,
                'old_price': old_price,
                'new_price': order_line.unit_price,
                }

            if old_price < order_line.unit_price:
                message = _(
                    "The unit price of product {product_name} increased from "
                    "{currency} {old_price:.2f} to {currency} {new_price:.2f}."
                    ).format(**vals)
            else:
                message = _(
                    "The unit price of product {product_name} dropped from "
                    "{currency} {old_price:.2f} to {currency} {new_price:.2f}."
                    ).format(**vals)
            flash(message)

        return order_line


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    def refresh_taxes(self):
        "Refresh taxes of sale line"
        pool = Pool()
        SaleLine = pool.get('sale.line')

        updated_sale = SaleLine(self.id).on_change_product()
        self.taxes = updated_sale.taxes
        self.save()

    def serialize(self, purpose=None):
        """
        Serialize SaleLine data
        """
        res = {}
        if purpose == 'cart':
            currency_format = partial(
                numbers.format_currency, currency=self.sale.currency.code,
                locale=current_locale.language.code
            )
            number_format = partial(
                numbers.format_decimal, locale=current_locale.language.code
            )
            res.update({
                'id': self.id,
                'display_name': (
                    self.product and self.product.name or self.description
                ),
                'url': self.product.get_absolute_url(_external=True),
                'image': (
                    self.product.default_image.transform_command().thumbnail(
                        150, 150, 'a'
                    ).url() if self.product.default_image else None
                ),
                'product': self.product.serialize(purpose),
                'quantity': number_format(self.quantity),
                'unit': self.unit.symbol,
                'unit_price': currency_format(self.unit_price),
                'amount': currency_format(self.amount),
                'remove_url': url_for(
                    'nereid.cart.delete_from_cart', line=self.id
                ),
            })
        elif hasattr(super(), 'serialize'):
            return super().serialize(purpose)  # pragma: no cover
        return res

    def add_to(self, sale):
        """
        Copy sale_line to new sale.

        Downstream modules can override this method to add change
        this behaviour of copying.

        :param sale: Sale active record.

        :return: Newly created sale_line
        """
        return sale._add_or_update(self.product.id, self.quantity)

    def validate_for_product_inventory(self):
        """
        This method validates the sale line against the product's inventory
        attributes. This method requires request context.
        """
        if has_request_context() and not self.product.can_buy_from_eshop():
            flash(_('This product is no longer available'))
            abort(redirect(request.referrer))
