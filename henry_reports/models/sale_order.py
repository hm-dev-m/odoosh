from odoo import api, fields, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def format_monetary_field(self, price):
        return formatLang(self.env, price, currency_obj=self.currency_id, digits=2)
