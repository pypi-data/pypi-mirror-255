# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool

from . import checkout, payment, sale, transaction

__all__ = ['register']


def register():
    Pool.register(
        checkout.Checkout,
        payment.Payment,
        transaction.PaymentGatewayPaypal,
        transaction.PaymentTransactionPaypal,
        sale.Sale,
        module='payment_gateway_paypal', type_='model')
