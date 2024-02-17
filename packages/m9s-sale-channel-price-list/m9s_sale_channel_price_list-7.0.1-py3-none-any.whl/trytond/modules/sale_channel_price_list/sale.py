# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    @classmethod
    def default_price_list(cls):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Channel = pool.get('sale.channel')

        channel_id = Sale.default_channel()
        if channel_id:
            channel = Channel(channel_id)
            if channel.price_list:
                return channel.price_list.id

    def set_price_list(self):
        # Until here super() sets the party price list or sales configuration
        # price list. So we set the channel price list if there is no party or
        # no price list on the party defined.
        if self.channel and self.channel.price_list:
            if not self.party or (
                    self.party and not self.party.sale_price_list):
                self.price_list = self.channel.price_list.id

    @fields.depends('channel', 'party')
    def on_change_channel(self):
        super().on_change_channel()
        self.set_price_list()

    @fields.depends('channel', 'party')
    def on_change_party(self):
        super().on_change_party()
        self.set_price_list()
