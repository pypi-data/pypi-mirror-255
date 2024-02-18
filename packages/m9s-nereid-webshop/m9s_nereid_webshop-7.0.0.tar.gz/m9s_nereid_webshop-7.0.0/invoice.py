# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import tempfile

from trytond.pool import Pool, PoolMeta

from nereid import abort, current_user, login_required, route
from nereid.helpers import send_file


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    @route('/orders/invoice/<int:active_id>/download')
    @login_required
    def download_invoice(self):
        """
        Allow user to download invoice.
        """
        Report = Pool().get('account.invoice', type='report')

        if self.party != current_user.party:
            abort(403)

        vals = Report.execute([self.id], {})
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(vals[1])
        return send_file(
            file.name,
            as_attachment=True,
            attachment_filename='.'.join([vals[3], vals[0]]),
        )
