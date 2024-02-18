# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

from nereid import redirect
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('payment_gateway_paypal')


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    @classmethod
    def get_payment_method_priority(cls):
        methods = super(Sale, cls).get_payment_method_priority()
        return methods + ('paypal',)
