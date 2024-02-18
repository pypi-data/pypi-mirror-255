# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta


class SaleChannel(metaclass=PoolMeta):
    __name__ = 'sale.channel'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        source = ('webshop', 'Webshop')
        if source not in cls.source.selection:
            cls.source.selection.append(source)
