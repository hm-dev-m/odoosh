
from odoo import models

class DatevExportCSV(models.AbstractModel):
    _inherit = 'account.general.ledger'

    def _get_reports_buttons(self, options):
        buttons = super(DatevExportCSV, self)._get_reports_buttons(options)
        button_count = 0
        for button in buttons:
            if button['name'] == 'Datev (zip)':
                del buttons[button_count]
            button_count += 1
        return buttons