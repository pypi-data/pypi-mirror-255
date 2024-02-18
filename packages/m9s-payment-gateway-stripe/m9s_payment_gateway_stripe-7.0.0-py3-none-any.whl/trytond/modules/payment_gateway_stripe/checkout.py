# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal

from trytond.modules.nereid_checkout.checkout import (
    not_empty_cart, sale_has_non_guest_party, with_company_context)
from trytond.pool import Pool, PoolMeta

from nereid import (
    current_website, flash, redirect, render_template, route, url_for)
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('payment_gateway_stripe')


class Checkout(metaclass=PoolMeta):
    __name__ = 'nereid.checkout'

    @classmethod
    def _process_credit_card_payment(cls, cart, credit_card_form):
        # Validate the credit card form and checkout using that
        # Only one payment per gateway
        gateway = current_website.credit_card_gateway
        if gateway.method == 'credit_card' and gateway.provider == 'stripe':
            sale = cart.sale
            payment = sale._get_payment_for_gateway(gateway)
            if payment is None:
                sale._add_sale_payment(credit_card_form=credit_card_form)
                payment = sale._get_payment_for_gateway(gateway)
            # Update the paymount_amount with the actual needed sum, when
            # it was set to 0 by a cancelation.
            if payment.amount == Decimal('0'):
                payment.amount = sale._get_amount_to_checkout()
                payment.save()
            payment_transaction = payment._create_payment_transaction(
                payment.amount, 'Payment by Card')
            payment_transaction.save()
            payment_transaction.create_payment_intent_stripe()
            client_secret = payment_transaction.provider_token
            sale.save()
            return redirect(url_for('nereid.checkout.stripe_checkout',
                    sale_id=sale.id, client_secret=client_secret))
        else:
            super()._process_credit_card_payment(cart, credit_card_form)

    @classmethod
    @route('/checkout/checkout_stripe/<sale_id>/<client_secret>',
        methods=['GET'])
    @not_empty_cart
    @sale_has_non_guest_party
    @with_company_context
    def stripe_checkout(cls, sale_id=None, client_secret=None):
        pool = Pool()
        Sale = pool.get('sale.sale')

        if not sale_id or not client_secret:
            return
        sale = Sale(sale_id)
        payment_gateway = current_website.credit_card_gateway
        return render_template(
            'checkout/checkout_stripe.jinja',
            sale=sale,
            payment_gateway=payment_gateway,
            client_secret=client_secret,
            )

    @classmethod
    @route('/checkout_stripe_form/<sale_id>/<client_secret>',
        methods=['GET'])
    def stripe_checkout_form(cls, sale_id=None, client_secret=None):
        '''
        Undecorated method allowing the call without cart.
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')

        if not sale_id or not client_secret:
            return
        sale = Sale(sale_id)
        payment_gateway = current_website.credit_card_gateway
        return render_template(
            'checkout/checkout_stripe.jinja',
            sale=sale,
            payment_gateway=payment_gateway,
            client_secret=client_secret,
            )

    @classmethod
    @route('/checkout/stripecancel/<sale_id>', methods=['GET'], readonly=False)
    @with_company_context
    def cancel_stripe_payment(cls, sale_id=None):
        '''
        Set the transaction to failed and return to payment options
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        GatewayTransaction = pool.get('payment_gateway.transaction')

        if sale_id:
            sale = Sale(sale_id)
            payment = None
            stripe = current_website.credit_card_gateway
            for s_payment in sale.payments:
                if s_payment.gateway.id == stripe.id:
                    payment = s_payment
                    break
            if payment:
                payment.amount = Decimal('0.0')
                payment.save()
                transactions = GatewayTransaction.search([
                    ('sale_payment', '=', payment.id),
                    ])
                for transaction in transactions:
                    transaction.state = 'cancel'
                    transaction.save()
            flash(_('Credit Card payment canceled'), 'info')
        else:
            flash(_('Error in processing payment.'), 'warning')
        return redirect(url_for('nereid.checkout.payment_method'))
