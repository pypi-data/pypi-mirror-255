# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal

from trytond.modules.nereid_checkout.checkout import with_company_context
from trytond.pool import Pool, PoolMeta

from nereid import flash, redirect, request, route, url_for
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('payment_gateway_paypal')


class Checkout(metaclass=PoolMeta):
    __name__ = 'nereid.checkout'

    @classmethod
    def _process_payment(cls, cart):
        pool = Pool()
        PaymentMethod = pool.get('nereid.website.payment_method')

        payment_form = cls.get_payment_form()
        sale = cart.sale

        if payment_form.alternate_payment_method.data:
            payment_method = PaymentMethod(
                    payment_form.alternate_payment_method.data)
            if payment_method.method == 'paypal':
                # Only one payment per gateway
                gateway = payment_method.gateway
                payment = sale._get_payment_for_gateway(gateway)
                if payment is None:
                    sale._add_sale_payment(
                        alternate_payment_method=payment_method)
                    payment = sale._get_payment_for_gateway(gateway)
                # Update the paymount_amount with the actual needed sum, when
                # it was set to 0 by a cancelation.
                if payment.amount == Decimal('0'):
                    payment.amount = sale._get_amount_to_checkout()
                    payment.save()
                payment_transaction = payment._create_payment_transaction(
                    payment.amount, str(_('Paid by PayPal')))
                payment_transaction.save()
                payment_transaction.authorize_paypal()
                return redirect(payment_transaction.approval_url)
        return super(Checkout, cls)._process_payment(cart)

    @classmethod
    @route('/checkout/paypalconfirm', methods=['GET'], readonly=False)
    @with_company_context
    def execute_paypal_payment(cls):
        '''
        Provide a return URL for the PayPal confirmation request

        - Update the transaction with the Payer ID (needed for later execution)
        - Set the payment_processing_state of the sale for further processing
          via the cron job
        '''
        pool = Pool()
        GatewayTransaction = pool.get('payment_gateway.transaction')
        TransactionLog = pool.get('payment_gateway.transaction.log')
        NereidCart = pool.get('nereid.cart')

        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')
        transactions = GatewayTransaction.search([
                ('provider_reference', '=', payment_id),
                ])
        if len(transactions) == 1:
            transaction = transactions[0]
            TransactionLog.create([{
                        'transaction': transaction,
                        'log': '%s\n\n%s' % (
                            'Callback paypalconfirm:',
                            str(request.args)),
                        }])
            if payer_id:
                transaction.customer_id = payer_id
                transaction.state = 'authorized'
                transaction.save()
                sale = transaction.sale_payment.sale
                sale.payment_processing_state = 'waiting_for_capture'
                sale.save()
                cart = NereidCart.open_cart()
                return cls.confirm_cart(cart)
            else:
                cls.restore_cart(transaction)
                flash(_('Error in payment processing'), 'warning')
                return redirect(url_for('nereid.checkout.payment_method'))
        else:
            flash(_('Error in payment processing'), 'warning')
            return redirect(url_for('nereid.checkout.payment_method'))

    @classmethod
    @route('/checkout/paypalcancel', methods=['GET'], readonly=False)
    @with_company_context
    def cancel_paypal_payment(cls):
        '''
        Set the transaction to failed and return to payment options
        '''
        pool = Pool()
        GatewayTransaction = pool.get('payment_gateway.transaction')
        TransactionLog = pool.get('payment_gateway.transaction.log')
        SalePayment = pool.get('sale.payment')

        token = request.args.get('token')
        transactions = GatewayTransaction.search([
                ('provider_token', '=', token),
                ])
        if len(transactions) == 1:
            transaction = transactions[0]
            TransactionLog.create([{
                        'transaction': transaction,
                        'log': '%s\n\n%s' % (
                            'Callback paypalcancel:',
                            str(request.args)),
                        }])
            transaction.state = 'cancel'
            transaction.save()
            payment = SalePayment(transaction.sale_payment.id)
            payment.amount = Decimal('0.0')
            payment.save()
            cls.restore_cart(transaction)
            flash(_('PayPal payment canceled'), 'info')
        else:
            flash(_('Error in payment processing'), 'warning')
        return redirect(url_for('nereid.checkout.payment_method'))

    @classmethod
    def restore_cart(cls, transaction):
        pool = Pool()
        NereidCart = pool.get('nereid.cart')

        # Reset the actual cart sale to the initial state
        sale = transaction.sale_payment.sale
        cart = NereidCart.open_cart()
        cart.sale = sale
        cart.save()
        cls._sanitize_payments(cart)

    @classmethod
    def confirm_cart(cls, cart, do_redirect=True):
        '''
        Confirm the cart only for successful Paypal payments.
         - Avoid to send confirmation mails
         - Avoid early processing of the sale
        '''
        sale = cart.sale
        # We can not check for any, because there could be other payments
        # with deferred payment (#2954).
        if sale:
            if (all(p.gateway.provider == 'paypal' for p in sale.payments)
                    and sale.payment_authorized != sale.payment_total):
                flash(_('Error in payment processing'), 'warning')
                return redirect(url_for('nereid.checkout.payment_method'))
        return super(Checkout, cls).confirm_cart(cart, do_redirect=do_redirect)
