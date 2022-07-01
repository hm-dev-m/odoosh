# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    datev_ascii_group_moves = fields.Boolean('Group Moves in DATEV ASCII Export')