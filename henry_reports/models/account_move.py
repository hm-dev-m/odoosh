from odoo import api, fields, models
from odoo.tools.misc import formatLang


class AccountMove(models.Model):

    _inherit = "account.move"

    def format_monetary_field(self, price=0.0):
        return formatLang(self.env, price, currency_obj=self.currency_id, digits=2)
