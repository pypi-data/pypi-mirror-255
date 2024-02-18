# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging
import os

from wtforms import StringField, validators

from trytond.config import config
from trytond.model import fields
from trytond.modules.nereid_base.party import AddressForm
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

from nereid import current_app, current_user, request
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('nereid_webshop')

geoip = None
try:
    from pygeoip import GeoIP
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("pygeoip is not installed")
else:
    path = os.environ.get(
        'GEOIP_DATA_PATH', config.get('nereid_webshop', 'geoip_data_path')
    )
    if path:
        geoip = GeoIP(path)


class WebshopAddressForm(AddressForm):
    """
    Custom address form for webshop
    """

    phone = StringField(_('Phone'), [validators.DataRequired(), ])

    def get_default_country(self):
        """Get the default country based on geoip data.
        """
        if not geoip or not request.remote_addr:
            return None

        Country = Pool().get('country.country')
        try:
            current_app.logger.debug(
                "GeoIP lookup for remote address: %s" % request.remote_addr
            )
            country, = Country.search([
                ('code', '=', geoip.country_code_by_addr(request.remote_addr))
            ])
        except ValueError:
            return None
        return country

    def __init__(self, formdata=None, **kwargs):

        # While choices can be assigned after the form is constructed, default
        # cannot be. The form's data is picked from the first available of
        # formdata and kwargs.
        # Once the data has been resolved, changing the default won't do
        # anything.
        default_country = self.get_default_country()
        if default_country:
            kwargs.setdefault('country', default_country.id)

        super(WebshopAddressForm, self).__init__(
            formdata, **kwargs)


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    shop_full_address = fields.Function(fields.Text('Shop Full Address'),
            'get_shop_full_address')

    def get_shop_full_address(self, name):
        with Transaction().set_context(address_with_party=True):
            return super(Address, self).get_full_address(name)

    @classmethod
    def get_address_form(cls, address=None):
        """
        Return an initialised Address form that can be validated and used to
        create/update addresses

        :param address: If an active record is provided it is used to autofill
                        the form.
        """
        if address:
            phone = address.party.contact_mechanism_get(
                types=['phone', 'mobile'], usage='web')
            form = WebshopAddressForm(
                request.form,
                name=address.party_name,
                street=address.street,
                postal_code=address.postal_code,
                city=address.city,
                country=address.country and address.country.id,
                subdivision=address.subdivision and address.subdivision.id,
                email=address.party.email,
                phone=phone.value if phone else None,
            )
        else:
            address_name = "" if current_user.is_anonymous else \
                current_user.name
            form = WebshopAddressForm(request.form, name=address_name)

        return form
