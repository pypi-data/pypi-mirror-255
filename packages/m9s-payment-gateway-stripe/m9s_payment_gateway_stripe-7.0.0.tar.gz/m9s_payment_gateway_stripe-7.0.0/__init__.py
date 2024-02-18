# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import checkout, party, transaction

__all__ = ['register']


def register():
    Pool.register(
        party.Address,
        party.PaymentProfile,
        party.Party,
        transaction.PaymentGatewayStripe,
        transaction.PaymentTransactionStripe,
        module='payment_gateway_stripe', type_='model')
    Pool.register(
        checkout.Checkout,
        depends=['nereid_checkout'],
        module='payment_gateway_stripe', type_='model')
    Pool.register(
        transaction.AddPaymentProfile,
        transaction.TransactionUseCard,
        module='payment_gateway_stripe', type_='wizard')
    Pool.register(
        transaction.AddSalePayment,
        depends=['sale_payment_gateway'],
        module='payment_gateway_stripe', type_='wizard')
