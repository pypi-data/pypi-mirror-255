# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import urllib.error
import urllib.parse
import urllib.request
import uuid

from decimal import Decimal
from itertools import groupby
from operator import attrgetter

import stripe

from trytond.exceptions import UserError
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval, Not
from trytond.transaction import Transaction
from trytond.url import HOSTNAME
from trytond.wizard import StateAction

stripe.api_version = '2019-05-16'


STATES = {
    'invisible': Eval('provider') != 'stripe',
    'readonly': Not(Bool(Eval('active'))),
    }
STATESR = {
        'required': Eval('provider') == 'stripe',
        }
STATESR.update(STATES)


class PaymentGatewayStripe(metaclass=PoolMeta):
    "Stripe Gateway Implementation"
    __name__ = 'payment_gateway.gateway'

    stripe_api_key = fields.Char('Stripe API Key',
        states=STATESR)
    stripe_publishable_key = fields.Char('Stripe Publishable Key',
        states=STATESR)
    stripe_webhook_identifier = fields.Char('Webhook Identifier', readonly=True)
    stripe_webhook_endpoint = fields.Function(fields.Char('Webhook Endpoint',
            help='The Webhook endpoint called by Stripe.'),
        'on_change_with_stripe_webhook_endpoint')
    stripe_webhook_signature_secret_key = fields.Char(
        'Webhook Signature Secret Key',
        states=STATES)
    stripe_check_zip_code = fields.Boolean('Check Zip Code',
        states=STATES)

    @classmethod
    def __setup__(cls):
        super(PaymentGatewayStripe, cls).__setup__()
        cls._buttons.update({
                'new_identifier': {
                    'icon': 'tryton-refresh',
                    },
                })
        #if Pool().test:
        #    cls.__rpc__['webhook'] = RPC(readonly=False, instantiate=0)

    @classmethod
    def get_providers(cls, values=None):
        """
        Downstream modules can add to the list
        """
        rv = super(PaymentGatewayStripe, cls).get_providers()
        stripe_record = ('stripe', 'Stripe')
        if stripe_record not in rv:
            rv.append(stripe_record)
        return rv

    @fields.depends('provider')
    def get_methods(self):
        if self.provider == 'stripe':
            return [
                ('credit_card', 'Credit Card - Stripe'),
            ]
        return super(PaymentGatewayStripe, self).get_methods()

    @classmethod
    def view_attributes(cls):
        return super(PaymentGatewayStripe, cls).view_attributes() + [(
            '//notebook/page[@id="stripe"]', 'states', {
                'invisible': Eval('provider') != 'stripe'
            }
        )]

    @classmethod
    @ModelView.button
    def new_identifier(cls, gateways):
        for gateway in gateways:
            gateway.stripe_webhook_identifier = uuid.uuid4().hex
        cls.save(gateways)

    @fields.depends('stripe_webhook_identifier')
    def on_change_with_stripe_webhook_endpoint(self, name=None):
        if not self.stripe_webhook_identifier:
            return ''
        # TODO add basic authentication support
        url_part = {
            'hook_path': '/checkout/webhook/stripe',
            'identifier': self.stripe_webhook_identifier,
            }
        return 'https://' + HOSTNAME + '/<default_locale>' + (
            urllib.request.pathname2url(
                '%(hook_path)s/%(identifier)s'
                % url_part))


class PaymentTransactionStripe(metaclass=PoolMeta):
    """
    Payment Transaction implementation for Stripe
    """
    __name__ = 'payment_gateway.transaction'
    stripe_amount = fields.Function(
        fields.Integer("Stripe Amount"),
        'get_stripe_amount', setter='set_stripe_amount')

    def get_stripe_amount(self, name):
        """
        Stripe requires amounts in currencies that support decimals to be
        multiplied by 100 while the other ones sent as such.

        https://stripe.com/docs/currencies#zero-decimal

        """
        #if self.currency.code in (
        #        'BIF', 'XAF', 'XPF', 'CLP',
        #        'KMF', 'DJF', 'GNF', 'JPY',
        #        'MGA', 'PYG', 'RWF', 'KRW',
        #        'VUV', 'VND', 'XOF'):
        #    return int(self.amount)
        return int(self.amount * 10 ** self.currency_digits)

    @classmethod
    def set_stripe_amount(cls, transactions, name, value):
        keyfunc = attrgetter('currency_digits')
        transactions = sorted(transactions, key=keyfunc)
        value = Decimal(value)
        for digits, transactions in groupby(transactions, keyfunc):
            digits = Decimal(digits)
            cls.write(list(transactions), {
                    'amount': value * 10 ** -digits,
                    })

    def create_payment_intent_stripe(self):
        """
        Create a payment intent.

        20190613:
            - Migrate to the PaymentIntent-Api needed
              for SCA conformity.
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        stripe.api_key = self.gateway.stripe_api_key

        payload = {
            'amount': self.stripe_amount,
            'currency': self.currency.code.lower(),
            'capture_method': 'automatic',
            'payment_method_types': ['card'],
            }

        try:
            intent = stripe.PaymentIntent.create(**payload)
        except (
            stripe.error.CardError, stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ) as exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            self.provider_reference = intent['id']
            self.provider_token = intent['client_secret']
            self.approval_url = intent['charges'].get('url', None)
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': str(intent),
            }])

    def authorize_stripe(self, card_info=None):
        """
        Authorize using stripe.

        20190613:
            - just set the state for compatibility behavior, we charge
              directly over the SCA-conform interface by stripe.js.
        """
        self.state = 'authorized'
        self.save()

    def settle_stripe(self):
        """
        Settle an authorized charge

        20190613:
            - just set the state for compatibility behavior, we charge
              directly over the SCA-conform interface by stripe.js.
        """
        self.state = 'completed'
        self.save()
        self.safe_post()

    def capture_stripe(self, card_info=None):
        """
        Capture using stripe.

        20190613:
            - just set the state for compatibility behavior, we charge
              directly over the SCA-conform interface by stripe.js.
        """
        self.state = 'completed'
        self.save()
        self.safe_post()

    def get_stripe_charge_data(self, card_info=None):
        """
        Downstream modules can modify this method to send extra data to
        stripe
        """
        charge_data = {
            'amount': self.stripe_amount,
            'currency': self.currency.code.lower(),
        }

        if card_info:
            charge_data['source'] = {
                'object': 'card',
                'number': card_info.number,
                'exp_month': card_info.expiry_month,
                'exp_year': card_info.expiry_year,
                'cvc': card_info.csc,
                'name': card_info.owner,
            }
            charge_data['source'].update(self.address.get_address_for_stripe())

        elif self.payment_profile:
            charge_data.update({
                'customer': self.payment_profile.stripe_customer_id,
                'card': self.payment_profile.provider_reference,
            })

        else:
            self.raise_user_error('no_card_or_profile')

        return charge_data

    def retry_stripe(self, credit_card=None):
        """
        Retry charge

        :param credit_card: An instance of CreditCardView
        """
        raise self.raise_user_error('feature_not_available')

    def update_stripe(self):
        """
        Update the status of the transaction from Stripe
        """
        raise self.raise_user_error('feature_not_available')

    def cancel_stripe(self):
        """
        Cancel this authorization or request
        """
        # TODO migrate to PaymentIntent-API
        raise self.raise_user_error('feature_not_available')

        TransactionLog = Pool().get('payment_gateway.transaction.log')

        if self.state != 'authorized':
            self.raise_user_error('cancel_only_authorized')

        stripe.api_key = self.gateway.stripe_api_key

        try:
            charge = stripe.Charge.retrieve(
                self.provider_reference
            ).refund(idempotency_key=('refund_%s' % self.uuid))
        except (
            stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ) as exc:
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            self.state = 'cancel'
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': str(charge),
            }])

    def refund_stripe(self):
        """
        Refund this authorization or request
        """
        # TODO migrate to PaymentIntent-API
        raise self.raise_user_error('feature_not_available')

        TransactionLog = Pool().get('payment_gateway.transaction.log')

        stripe.api_key = self.gateway.stripe_api_key

        try:
            refund = stripe.Refund.create(
                charge=self.origin.provider_reference,
                amount=self.stripe_amount
            )
        except (
            stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ) as exc:
            self.state = 'failed'
            self.save()
            TransactionLog.serialize_and_create(self, exc.json_body)
        else:
            self.provider_reference = refund.id
            self.state = 'completed'
            self.save()
            TransactionLog.create([{
                'transaction': self,
                'log': str(refund),
            }])
            self.safe_post()


# TODO Move this to party
class AddPaymentProfile(metaclass=PoolMeta):
    """
    Add a payment profile
    """
    __name__ = 'party.party.payment_profile.add'

    def transition_add_stripe(self):
        """
        Handle the case if the profile should be added for Stripe
        """
        card_info = self.card_info

        stripe.api_key = card_info.gateway.stripe_api_key

        profile_data = {
            'source': {
                'object': 'card',
                'number': card_info.number,
                'exp_month': card_info.expiry_month,
                'exp_year': card_info.expiry_year,
                'cvc': card_info.csc,
                'name': card_info.owner,
            },
        }
        profile_data['source'].update(
            card_info.address.get_address_for_stripe())

        customer_id = card_info.party._get_stripe_customer_id(
            card_info.gateway
        )

        try:
            if customer_id:
                customer = stripe.Customer.retrieve(customer_id)
                card = customer.sources.create(**profile_data)
            else:
                profile_data.update({
                    'description': card_info.party.name,
                    'email': card_info.party.email,
                })
                customer = stripe.Customer.create(**profile_data)
                card = customer.sources.data[0]
        except (
            stripe.error.CardError, stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError, stripe.error.APIConnectionError,
            stripe.error.StripeError
        ) as exc:
            raise UserError(exc.json_body['error']['message'])

        return self.create_profile(
            card.id,
            stripe_customer_id=customer.id
        )


class AddSalePayment(metaclass=PoolMeta):
    __name__ = 'sale.payment.add'

    checkout_stripe = StateAction('payment_gateway_stripe.url_checkout')

    def transition_finish(self):
        if self.payment_info.gateway.provider == 'stripe':
            return 'checkout_stripe'
        return super().transition_finish()

    def do_checkout_stripe(self, action):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Website = pool.get('nereid.website')

        context = Transaction().context
        active_model = context['active_model']
        active_id = context['active_id']
        if active_model == Sale.__name__:
            Model = Sale
        #elif active_model == Payment.__name__:
        #    Model = Payment
        else:
            raise ValueError("Invalid active_model: %s" % active_model)
        record = Model(active_id)

        payment, = [p for p in record.payments
            if p.gateway == self.payment_info.gateway]
        trx = payment._create_payment_transaction(self.payment_info.amount,
            payment.description)
        trx.save()
        trx.create_payment_intent_stripe()

        website, = Website.search([], limit=1)
        locale = website.default_locale.language.code
        secure = True
        action['url'] = action['url'] % {
            'protocol': 'https' if secure else 'http',
            'hostname': HOSTNAME,
            'port': '443' if secure else '80',
            'locale': locale,
            'sale': active_id,
            'client_secret': trx.provider_token,
            }
        return action, {}


class TransactionUseCard(metaclass=PoolMeta):
    __name__ = 'payment_gateway.transaction.use_card'

    checkout_stripe = StateAction('payment_gateway_stripe.url_checkout')

    def transition_capture(self):
        """
        Delegate for stripe to the credit card checkout and let manually
        capture.
        """
        PaymentTransaction = Pool().get('payment_gateway.transaction')
        trx = PaymentTransaction(Transaction().context.get('active_id'))

        if trx.gateway.provider == 'stripe':
            return 'checkout_stripe'
        return super().transition_capture()

    def do_checkout_stripe(self, action):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Website = pool.get('nereid.website')
        PaymentTransaction = pool.get('payment_gateway.transaction')

        trx = PaymentTransaction(Transaction().context.get('active_id'))
        if isinstance(trx.origin, Sale):
            sale = trx.origin
            trx.create_payment_intent_stripe()
            website, = Website.search([], limit=1)
            locale = website.default_locale.language.code
            secure = True
            action['url'] = action['url'] % {
                'protocol': 'https' if secure else 'http',
                'hostname': HOSTNAME,
                'port': '443' if secure else '80',
                'locale': locale,
                'sale': sale.id,
                'client_secret': trx.provider_token,
                }
            return action, {}
