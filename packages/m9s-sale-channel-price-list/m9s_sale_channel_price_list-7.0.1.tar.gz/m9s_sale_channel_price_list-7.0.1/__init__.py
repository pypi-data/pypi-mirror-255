# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import channel, sale

__all__ = ['register']


def register():
    Pool.register(
        channel.SaleChannel,
        sale.Sale,
        module='sale_channel_price_list', type_='model')
