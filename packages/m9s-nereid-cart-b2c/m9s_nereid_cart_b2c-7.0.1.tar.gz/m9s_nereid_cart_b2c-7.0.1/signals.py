# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from flask.signals import _signals

#: Cart update signal
#:  - This signal is triggered when a the cart is updated.
cart_updated = _signals.signal('cart-updated')
