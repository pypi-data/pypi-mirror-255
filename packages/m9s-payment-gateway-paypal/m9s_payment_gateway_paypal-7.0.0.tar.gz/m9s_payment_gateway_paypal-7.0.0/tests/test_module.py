# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class PaymentGatewayPaypalTestCase(ModuleTestCase):
    "Test Payment Gateway Paypal module"
    module = 'payment_gateway_paypal'


del ModuleTestCase
