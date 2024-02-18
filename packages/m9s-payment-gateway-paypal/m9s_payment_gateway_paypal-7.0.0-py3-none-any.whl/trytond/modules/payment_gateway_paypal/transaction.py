# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging

from urllib.parse import parse_qs, urlparse

import paypalrestsdk

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Not

from nereid import url_for
from nereid.ctx import has_request_context

logger = logging.getLogger(__name__)
#logger.level = 'debug'


class PaymentGatewayPaypal(metaclass=PoolMeta):
    'Paypal Gateway Implementation'
    __name__ = 'payment_gateway.gateway'

    paypal_mode = fields.Selection([
            ('sandbox', 'sandbox'),
            ('live', 'live')
            ], 'Paypal Mode',
        help='The Paypal API mode (testing or live).')
    paypal_client_id = fields.Char(
        'Paypal Client ID', states={
            'required': Eval('provider') == 'paypal',
            'invisible': Eval('provider') != 'paypal',
            'readonly': Not(Bool(Eval('active'))),
        })
    paypal_client_secret = fields.Char(
        'Paypal Client Secret', states={
            'required': Eval('provider') == 'paypal',
            'invisible': Eval('provider') != 'paypal',
            'readonly': Not(Bool(Eval('active'))),
        })

    @classmethod
    def view_attributes(cls):
        return super(PaymentGatewayPaypal, cls).view_attributes() + [
            ('//notebook/page[@id="paypal"]', 'states', {
                    'invisible': Eval('provider') != 'paypal',
                    }),
            ]

    @staticmethod
    def default_paypal_mode():
        return 'sandbox'

    @classmethod
    def get_providers(cls, values=None):
        rv = super(PaymentGatewayPaypal, cls).get_providers()
        paypal_record = ('paypal', 'Paypal')
        if paypal_record not in rv:
            rv.append(paypal_record)
        return rv

    @fields.depends('provider')
    def get_methods(self):
        if self.provider == 'paypal':
            return [
                ('paypal', 'Paypal'),
            ]
        return super(PaymentGatewayPaypal, self).get_methods()

    @classmethod
    def copy(cls, gateways, default=None):
        if default is None:
            default = {}
        default['paypal_mode'] = 'sandbox'
        return super(PaymentGatewayPaypal, cls).copy(gateways, default=default)


class PaymentTransactionPaypal(metaclass=PoolMeta):
    '''
    Payment Transaction implementation for Paypal
    '''
    __name__ = 'payment_gateway.transaction'

    approval_url = fields.Char('Approval URL', readonly=True)
    customer_id = fields.Char('Customer ID', readonly=True)
    provider_token = fields.Char('Provider Token', readonly=True)

    def get_paypalrestsdk_configuration(self):
        '''
        Configure the REST-SDK.
        '''
        return {
            'mode': self.gateway.paypal_mode,
            'client_id': self.gateway.paypal_client_id,
            'client_secret': self.gateway.paypal_client_secret,
            }

    def authorize_paypal(self, card_info=None):
        '''
        Authorize (create) a PayPal charge.
        '''
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        # Only create PayPal payments when called from the web, otherwise
        # do not try to authorize from Tryton
        if not has_request_context():
            sale = self.sale_payment.sale
            sale.payment_processing_state = None
            sale.save()
            self.state = 'cancel'
            self.save()
            return

        paypalrestsdk.configure(self.get_paypalrestsdk_configuration())
        charge_data = self.get_paypal_charge_data(card_info=card_info)
        payment = paypalrestsdk.Payment(charge_data)

        try:
            payment.create()
            logger.debug('Payment [%s] created successfully' % (payment.id))
        except Exception as exc:
            logger.info(payment.error)
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc)
        else:
            self.state = 'in-progress'
            self.approval_url = 'https://paypal.com'
            for link in payment.links:
                if link.method == 'REDIRECT':
                    # Convert to str to avoid google appengine unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    self.approval_url = str(link.href)
            logger.debug('Redirect for approval: %s' % (self.approval_url))
            params = parse_qs(urlparse(self.approval_url).query)
            token = params.get('token')
            if token:
                token, = token
            self.provider_reference = payment['id']
            self.provider_token = token
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': str(payment),
            }])

    def settle_paypal(self):
        '''
        Settle (execute) an authorized PayPal charge.
        '''
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        assert self.state == 'authorized'

        if self.provider_reference:
            paypalrestsdk.configure(self.get_paypalrestsdk_configuration())
            payment = paypalrestsdk.Payment.find(self.provider_reference)
        try:
            payment.execute({'payer_id': self.customer_id})
            logger.debug('Payment[%s] executed successfully' % (payment.id))
        except Exception as exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc)
        else:
            self.state = 'completed'
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': str(payment),
            }])
            self.safe_post()

    def capture_paypal(self, card_info=None):
        '''
        Capture not used with PayPal.
        '''
        pass

    def get_paypal_charge_data(self, card_info=None):
        '''
        Downstream modules can modify this method to send extra data to
        paypal
        '''
        sale = self.sale_payment.sale
        return_url = url_for('nereid.checkout.execute_paypal_payment',
            _external=True)
        cancel_url = url_for('nereid.checkout.cancel_paypal_payment',
            _external=True)
        address = sale.shipment_address

        charge_data = {
            'intent': 'sale',
            'payer': {
                'payment_method': 'paypal',
                #'payer_info': {
                #    'tax_id_type': 'ustid',
                #    'tax_id': 'DE12345678456',
                #    }
                },
            'redirect_urls': {
                'return_url': return_url,
                'cancel_url': cancel_url,
                },
            'transactions': [
                {
                    'amount': {
                        'total': str(self.sale_payment.amount),
                        'currency': self.currency.code.upper(),
                        #'details': {
                        #    'subtotal': str(sale.untaxed_amount),
                        #    'tax': str(sale.tax_amount),
                        #    'shipping': '7.50',
                        #    'handling_fee': '2.00',
                        #    },
                        },
                    'description': '%s %s (%s)' % ('Sale ID:', sale.id,
                        sale.party.rec_name),
                    #'custom': 'PP_EMS_90048630024435',
                    #'invoice_number': '48787589677',
                    'payment_options': {
                        'allowed_payment_method': 'INSTANT_FUNDING_SOURCE'
                    },
                    'soft_descriptor': self.uuid,
                    'item_list': {
                        #'items': [
                        #    {
                        #        'name': 'item',
                        #        'description': 'my item',
                        #        'quantity': '1',
                        #        'sku': 'item',
                        #        'price': '10.00',
                        #        'tax': '1.90',
                        #        'currency': 'EUR',
                        #        },
                        #    ],
                        'shipping_address': {
                            'recipient_name': address.party_full_name,
                            'line1': address.street,
                            'city': address.city,
                            'postal_code': address.postal_code,
                            'country_code': (address.country.code.upper()
                                or None),
                            },
                        },
                    },
                ],
                }
        return charge_data

    def retry_paypal(self, credit_card=None):
        '''
        Retry charge
        '''
        raise self.raise_user_error('feature_not_available')

    def update_paypal(self):
        '''
        Update the status of the transaction from Paypal
        '''
        raise self.raise_user_error('feature_not_available')

    def cancel_paypal(self):
        '''
        Cancel this authorization or request
        '''
        if self.state in ['draft', 'in-progress']:
            self.state = 'cancel'
            self.save()
        else:
            raise self.raise_user_error('cancel_not_allowed')

    def refund_paypal(self):
        raise self.raise_user_error('feature_not_available')
