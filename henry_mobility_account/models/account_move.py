from odoo import api, models, fields, api, _
from odoo.addons.account_inter_company_rules.models.account_move import AccountMove as AccountMoveOrigin


def _post(self, soft=True):
    """
        OVERRIDE function _post() changes from /addons/account_inter_company_rules/models/account_move.py .
    """
    invoices_map = {}
    posted = super(AccountMoveOrigin, self)._post(soft)
    for invoice in posted.filtered(lambda move: move.is_invoice()):
        company = self.env['res.company']._find_company_from_partner(invoice.partner_id.id)
        if company and company.rule_type == 'invoice_and_refund' and not invoice.auto_generated:
            invoices_map.setdefault(company, self.env['account.move'])
            invoices_map[company] += invoice
    for company, invoices in invoices_map.items():
        context = dict(self.env.context, default_company_id=company.id)
        context.pop('default_journal_id', None)

        # Start Update: generate a new invoice if it is not yet generated, else update the existing one.
        for invoice in invoices:
            inter_com_invoice = self.env['account.move'].with_user(company.intercompany_user_id).search([
                ('auto_invoice_id', '=', invoice.id), ('company_id', '=', company.id),
                ('state', 'in', ['draft', 'posted'])])
            if inter_com_invoice:
                invoice.with_context(context).with_company(company)._inter_company_update_invoice(inter_com_invoice)
            else:
                invoice.with_user(company.intercompany_user_id).with_context(context).with_company(company). \
                    _inter_company_create_invoices()

        # End Update
    return posted


AccountMoveOrigin._post = _post


class AccountMove(models.Model):
    _inherit = 'account.move'

    # --------------------------------------------------------------------
    # METHODS
    # --------------------------------------------------------------------

    def _inter_company_update_invoice(self, invoice_to_update):
        """
        :param invoice_to_update: The invoice to be updated
        :return: the invoice after Update
        """

        self.ensure_one()

        # Make the invoice draft, if it is already posted
        if invoice_to_update.state == 'posted':
            invoice_to_update.button_draft()

        # 1- Prepare invoice new values.
        invoice_vals = self._inter_company_prepare_invoice_data(invoice_to_update.move_type)

        # 2- Prepare Invoice lines new values
        invoice_vals['invoice_line_ids'] = []
        for line in self.invoice_line_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, line._inter_company_prepare_invoice_line_data()))

        inv_new = self.with_context(default_move_type=invoice_vals['move_type']).new(invoice_vals)

        for line in inv_new.invoice_line_ids:
            # We  adapt the taxes following the fiscal position, but we must keep the price unit.
            price_unit = line.price_unit
            line.tax_ids = line._get_computed_taxes()
            line._set_price_and_tax_after_fpos()
            line.price_unit = price_unit

        invoice_vals = inv_new._convert_to_write(inv_new._cache)
        invoice_vals.pop('line_ids', None)
        invoice_vals.pop('journal_id', None)

        invoice_type = invoice_vals['move_type']

        # Update Invoice
        msg = _("Automatically Updated after %(origin)s of company %(company)s has been updated.", origin=self.name,
                company=self.company_id.name)
        invoice_to_update.with_context(default_type=invoice_type).write(invoice_vals)
        invoice_to_update.message_post(body=msg)

        return invoice_to_update
