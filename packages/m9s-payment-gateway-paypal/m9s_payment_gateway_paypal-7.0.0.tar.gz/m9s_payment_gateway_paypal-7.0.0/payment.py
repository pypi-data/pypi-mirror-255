# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('payment_gateway_paypal')


class Payment(metaclass=PoolMeta):
    __name__ = 'sale.payment'

    @fields.depends('method')
    def on_change_with_description(self, name=None):
        if self.method == 'paypal':
            return str(_('Paid by PayPal'))
        return super().on_change_with_description(name)
