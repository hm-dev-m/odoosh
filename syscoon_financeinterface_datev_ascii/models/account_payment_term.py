# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    datev_payment_conditons_id = fields.Integer('DATEV Payment Term ID')
