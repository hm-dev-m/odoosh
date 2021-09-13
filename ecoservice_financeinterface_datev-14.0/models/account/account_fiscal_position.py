# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import api, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    # region CRUD

    def write(self, vals):
        destination_accounts = self._get_destination_accounts(
            vals.get('account_ids'),
        )
        if 'vat_required' in vals:
            if destination_accounts:
                destination_accounts.write({
                    'datev_vat_handover': vals['vat_required'],
                })
            # Note: account_ids._name == 'account.fiscal.position.account'
            self.mapped('account_ids.account_dest_id').write({
                'datev_vat_handover': vals['vat_required'],
            })
        else:
            if destination_accounts:
                # TODO clarify: does this even make sense?
                for fiscal_position in self:
                    destination_accounts.write({
                        'datev_vat_handover': fiscal_position.vat_required,
                    })

        return super().write(vals)

    @api.model_create_single
    def create(self, vals):  # pyright: reportIncompatibleMethodOverride=false
        if vals.get('vat_required'):
            destination_accounts = self._get_destination_accounts(
                vals.get('account_ids'),
            )
            if destination_accounts:
                destination_accounts.write({
                    'datev_vat_handover': True,
                })
        return super().create(vals)

    # endregion

    # region Business Methods

    def _get_destination_accounts(self, account_ids: list):
        """
        Take account.fiscal.position.account and extract the destinations.

        :param account_ids: A list of account.fiscal.position.account
        :return: A recordset of the destination accounts. Can be empty.
        """
        account_model = self.env['account.account']

        if not account_ids:
            return account_model

        return account_model.browse([
            account[2]['account_dest_id']
            for account in account_ids if account[2]
        ])

    # endregion
