# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from flask_wtf import FlaskForm as Form
from wtforms import FloatField, IntegerField, validators

from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('nereid_cart_b2c')
_VDTR = [validators.DataRequired(message=_("This field is required"))]


class AddtoCartForm(Form):
    """
    A simple add to cart form
    """
    quantity = FloatField(_('Quantity'), default=1.0, validators=_VDTR)
    product = IntegerField(_('Product'), validators=_VDTR)
