# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import date

from dateutil.relativedelta import relativedelta

from trytond.cache import Cache
from trytond.config import config
from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Not
from trytond.transaction import Transaction

from nereid import (
    abort, current_locale, current_user, current_website, jsonify, route)
from nereid.contrib.locale import make_lazy_gettext
from nereid.helpers import key_from_list

_ = make_lazy_gettext('nereid_cart_b2c')

price_digits = (16, config.getint('product', 'price_decimal', default=4))


class Product(metaclass=PoolMeta):
    __name__ = "product.product"

    # TODO: Move these fields into webshop channel listing
    display_available_quantity = fields.Boolean(
        "Display Available Quantity On Website?"
    )

    start_displaying_available_quantity = fields.Numeric(
        'Start Quantity', digits=price_digits,
        states={
            'required': Bool(Eval('display_available_quantity')),
            'invisible': ~Bool(Eval('display_available_quantity')),
        }, depends=[
            'display_available_quantity',
        ],
        help=(
            "Product's available quantity must be less than this to show on"
            " website"
        )
    )

    min_warehouse_quantity = fields.Float(
        'Min Warehouse Quantity',
        help="Minimum quantity required in warehouse for orders\n\n"
            'Set None for Out of Stock.'

    )
    is_backorder = fields.Function(
        fields.Boolean("Is Backorder"), getter="get_is_backorder"
    )

    def get_is_backorder(self, name):
        if self.min_warehouse_quantity is None or \
                self.min_warehouse_quantity < 0:
            return True
        return False

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('//page[@id="customers"]', 'states', {
                    'invisible': Not(Bool(Eval('displayed_on_eshop')))
                    }),
            ]

    @classmethod
    def validate(cls, records):
        """
        Validation method
        """
        super().validate(records)

        for record in records:
            record.validate_start_display_quantity()

    def validate_start_display_quantity(self):
        """
        This method validates that `start_displaying_available_quantity` is
        always positive.
        """
        if self.start_displaying_available_quantity and \
                self.start_displaying_available_quantity <= 0:
            raise UserError(
                gettext('nereid_cart_b2c.start_displaying_positive'))

    @staticmethod
    def default_min_warehouse_quantity():
        """
        By default, min_warehouse_quantity is minus one. This is to handle the
        normal sale order workflow.
        """
        return -1.0

    def can_buy_from_eshop(self, quantity=None):
        """
        This function is used for inventory checking purpose. It returns a
        boolean result on the basis of fields such as min_warehouse_quantity.
        """
        if quantity is None:
            quantity = self.get_availability().get('quantity')

        if self.type != 'goods':
            # If product type is not goods, then inventory need not be checked
            return True

        if ((self.min_warehouse_quantity and self.min_warehouse_quantity < 0)
                or self.min_warehouse_quantity is None):
            # If min_warehouse_quantity is negative (back order) or not set,
            # product is in stock
            return True
        elif quantity > self.min_warehouse_quantity:
            # If min_warehouse_quantity is less than available quantity, product
            # is in stock
            return True
        else:
            # In all other cases, product is not in stock
            return False

    def inventory_status(self):
        """
        This method returns the inventory status for the given product which can
        have the following messages -:
          * Out Of Stock
          * In Stock
          * X <UOM> left

        It returns a tuple of the form -:
          ('in_stock', 'In Stock')
        whose elements are decided by the fields min_warehouse_quantity,
        start_displaying_available_quantity and the product's current quantity.

        The first element of the tuple can be used in future to decide things
        such as color scheming in template. The second element of the tuple is
        the message to show.
        """
        quantity = self.get_availability().get('quantity')

        if self.can_buy_from_eshop(quantity=quantity):
            status, message = 'in_stock', str(_('In stock'))
        else:
            status, message = 'out_of_stock', str(_('Out of stock'))

        quantity = int(quantity)
        if status == 'in_stock' and self.display_available_quantity and \
                quantity <= self.start_displaying_available_quantity:
            if self.min_warehouse_quantity > 0:
                quantity = quantity - self.min_warehouse_quantity

            message = '%s %s %s' % (quantity, self.default_uom.name,
                                    str(_('left')))

        return status, message

    def serialize(self, purpose=None):
        """
        Serialize product data
        """
        if purpose == 'cart':
            return {
                'id': self.id,
                'code': self.code,
                'name': self.name,
                'category': [category.name for category in self.categories],
                'image': (self.default_image.transform_command().thumbnail(
                    150, 150, 'a'
                ).url() if self.default_image else None),
            }
        if hasattr(super(), 'serialize'):
            return super().serialize(purpose)

    '''
    Provide short lived caches for product prices

    A cache duration of 10 min should be adequate for returning requests inside
    one session, this will also be the delay for evtl. occuring price updates
    '''
    _sale_price_cache = Cache('product.product.sale_price', duration=10 * 60)

    def sale_price(self, quantity=0):
        """Return the Sales Price.
        A wrapper designed to work as a context variable in templating

        The price is calculated from the pricelist associated with the current
        user. The user in the case of guest user is logged in user. In the
        event that the logged in user does not have a pricelist set against
        the user, the guest user's pricelist is chosen.

        Finally if neither the guest user, nor the registered user has a
        pricelist set against them then the list price is displayed as the
        list price of the product

        :param quantity: Quantity
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        Product = pool.get('product.product')

        context = {}
        if current_user.is_anonymous:
            context['customer'] = current_website.guest_user.party
        else:
            context['customer'] = current_user.party.id
        price_list = Sale.default_price_list()
        context['price_list'] = price_list
        context['currency'] = current_locale.currency.id

        price = self._sale_price_cache.get(self.id)
        if price is not None:
            return price
        with Transaction().set_context(context):
            price = Product.get_sale_price(
                [self], abs(quantity or 0))[self.id]
        self._sale_price_cache.set(self.id, price)
        return price

    def get_availability(self):
        """
        This method could be subclassed to implement your custom availability
        behavior.

        By default the forecasted quantity is a 7 day forecast. In future this
        feature may be replaced with a configuration value on the website to
        specify the number of days to forecast.

        .. warning::
            `quantity` is mandatory information which needs to be returned, no
            matter what your logic for computing that is

        :return: A dictionary with `quantity` and `forecast_quantity`
        """
        context = {
            'locations': [current_website.stock_location.id],
            'stock_date_end': date.today() + relativedelta(days=7)
        }
        with Transaction().set_context(**context):
            return {
                'quantity': self.get_quantity([self], 'quantity')[self.id],
                'forecast_quantity': self.get_quantity(
                    [self], 'forecast_quantity'
                )[self.id],
            }

    @classmethod
    @route('/product-availability/<uri>')
    def availability(cls, uri):
        """
        Returns the following information for a product:

        +-------------------+-----------------------------------------------+
        | quantity          | Available readily to buy                      |
        +-------------------+-----------------------------------------------+
        | forecast_quantity | Forecasted quantity, if the site needs it     |
        +-------------------+-----------------------------------------------+

        .. note::
            To modify the availability, or to send any additional information,
            it is recommended to subclass the :py:meth:`~get_availability` and
            implement your custom logic. For example, you might want to check
            stock with your vendor for back orders or send a message like
            `Only 5 pieces left`

        :param uri: URI of the product for which the availability needs to
                    be found
        :return: JSON object
        """
        try:
            product, = cls.search([
                ('displayed_on_eshop', '=', True),
                ('uri', '=', uri),
            ])
        except ValueError:
            return abort(404)

        return jsonify(product.get_availability())
