# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class PaymentGatewayStripeTestCase(ModuleTestCase):
    "Test Payment Gateway Stripe module"
    module = 'payment_gateway_stripe'


del ModuleTestCase
