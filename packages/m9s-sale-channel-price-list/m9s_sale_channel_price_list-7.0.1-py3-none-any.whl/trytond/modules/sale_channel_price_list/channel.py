# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta


class SaleChannel(metaclass=PoolMeta):
    __name__ = 'sale.channel'

    price_list = fields.Many2One('product.price_list', 'Price List')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.price_list.states = cls.company.states
