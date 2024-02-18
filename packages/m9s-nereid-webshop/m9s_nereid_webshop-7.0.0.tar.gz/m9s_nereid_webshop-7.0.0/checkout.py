# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import json

from decimal import Decimal

from werkzeug.wrappers import Response
from wtforms import StringField

from trytond.i18n import gettext
from trytond.modules.nereid_checkout.checkout import (
    PaymentForm, not_empty_cart, sale_has_non_guest_party)
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

from nereid import (
    current_website, flash, redirect, render_template, request, route, url_for)
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('nereid_webshop')


class GiftCardPaymentForm(PaymentForm):
    '''
    Form to capture additional payment data

    inherited from nereid_checkout
    '''
    gift_card_number = StringField(_('Gift Card Number'))


class Checkout(metaclass=PoolMeta):
    __name__ = 'nereid.checkout'

    @classmethod
    def get_form_payment(cls):
        '''
        Return a payment form
        '''
        return GiftCardPaymentForm()

    @classmethod
    def _process_payment(cls, cart):
        pool = Pool()
        PaymentMethod = pool.get('nereid.website.payment_method')
        GiftCard = pool.get('gift_card.gift_card')

        payment_form = cls.get_payment_form()

        if payment_form.alternate_payment_method.data:
            payment_method = PaymentMethod(
                    payment_form.alternate_payment_method.data)
            if payment_method.method == 'gift_card':
                gift_cards = GiftCard.search([
                        ('number', '=', payment_form.gift_card_number.data),
                        ('state', '=', 'active'),
                        ], limit=1)
                if not gift_cards:
                    flash(
                        _('No active gift card certificate '
                            'found for the given number.'),
                        'Error')
                    return redirect(url_for('nereid.checkout.payment_method'))
                gift_card = gift_cards[0]
                with Transaction().set_context(gift_card=gift_card.id):

                    # Only one payment per gateway and gift_card
                    gateway = payment_method.gateway
                    sale = cart.sale
                    rv = None
                    payment = sale._get_payment_for_gateway(gateway)
                    if payment is None:
                        rv = sale._add_sale_payment(
                            alternate_payment_method=payment_method)
                        payment = sale._get_payment_for_gateway(gateway)
                    # Update the paymount_amount with the actual needed sum,
                    # when it was set to 0 by a cancelation.
                    if payment.amount == Decimal('0'):
                        payment.amount = sale._get_amount_to_checkout()
                        payment.save()
                    payment_transaction = payment._create_payment_transaction(
                        payment.amount, str(_('Paid by Gift Card')))
                    payment_transaction.save()
                    payment.authorize()
                    if isinstance(rv, Response):
                        # If the alternate payment method introduced a
                        # redirect, then save the order and go to that
                        cls.confirm_cart(cart)
                        return rv
                    amount_to_pay = cart.sale._get_amount_to_checkout()
                    if amount_to_pay <= 0:
                        return cls.confirm_cart(cart)
                    flash(_('Payment by Gift Card with amount '
                            '%(amount)s registered.', amount=payment.amount))
                    return redirect(url_for('nereid.checkout.payment_method'))

        return super(Checkout, cls)._process_payment(cart)

    @classmethod
    @route('/checkout/delivery-method', methods=['GET', 'POST'])
    @not_empty_cart
    @sale_has_non_guest_party
    def delivery_method(cls):
        '''
        Override nereid_checkout:

        Selection of delivery method (options)

        Based on the shipping address selected, the delivery options
        could be shown to the user. This may include choosing shipping speed
        and if there are multiple items, the option to choose items as they are
        available or all at once.
        '''
        pool = Pool()
        NereidCart = pool.get('nereid.cart')
        Carrier = pool.get('carrier')
        Currency = pool.get('currency.currency')

        cart_sale = NereidCart.open_cart().sale

        if not cart_sale.shipment_address:
            return redirect(url_for('nereid.checkout.shipping_address'))

        errors = []
        if request.method == 'POST':
            if request.form.get('carrier_json'):
                rate = json.loads(request.form.get('carrier_json'))
                rate.update({
                    'carrier': Carrier(rate['carrier']),
                    'cost_currency': Currency(rate['cost_currency']),
                    'cost': Decimal("%s" % (rate['cost'], ))
                })
                cart_sale.apply_shipping_rate(rate)
                return redirect(url_for('nereid.checkout.payment_method'))
            else:
                msg = gettext('nereid_webshop.msg_no_carrier_selected')
                errors.append(msg)

        delivery_rates = []
        # Request only configured (website) and available (carrier_selection)
        # carriers.
        # Preserve the sequence in available_carriers to get later
        # the correct default carrier. Therefore use dict instead of set.
        website_carriers = set([c.id for c in current_website.carriers])
        available_carriers = {}
        for number, carrier in enumerate(cart_sale.available_carriers):
            available_carriers[number] = carrier

        carriers = []
        for carrier in available_carriers.values():
            if carrier.id in website_carriers:
                carriers.append(carrier)

        delivery_rates = cart_sale.get_shipping_rates(carriers)
        for rate in delivery_rates:
            if rate.get('errors'):
                errors.append(rate['errors'])
            if not rate.get('comment'):
                comment = rate['carrier'].delivery_comment
                if comment:
                    rate['comment'] = comment.replace('\\n', '\n')
        if errors:
            for error in errors:
                error = error.replace('\n',' ')
                flash(error, 'warning')

        return render_template(
            'checkout/delivery_method.jinja', delivery_rates=delivery_rates,
            sale=cart_sale)
