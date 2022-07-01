# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, fields, _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = 'res.company'

    datev_auto_set_accounts = fields.Selection(selection_add=[('skr04', 'SKR04')])

    def set_datev_skr04(self):
        self.env['account.tax']._set_taxkeys_skr04(self.id)
        self.env['account.account']._set_account_autoaccount_skr04(self.id)
        return

    def write(self, vals):
        for company in self:
            if not company.datev_auto_set_accounts and 'datev_auto_set_accounts' in vals and vals['datev_auto_set_accounts'] == 'skr04':
                if len(self) == 1:
                    company.set_datev_skr04()#
                else:
                    raise UserError(_('You try to update the accounts for more than one company at the same time. This is not possible. Please contact your Administrator.'))
        return super(Company, self).write(vals)
