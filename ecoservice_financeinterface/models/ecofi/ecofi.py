# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import base64
import csv
import io
from decimal import Decimal

from odoo import _, exceptions, fields, models


class Ecofi(models.Model):
    _name = 'ecofi'
    _description = 'ecoservice Finance Interface'
    _order = 'id desc'

    # region Fields

    name = fields.Char(
        string='Exportname',
        required=True,
        readonly=True,
    )
    journale = fields.Char(
        string='Journals',
        required=True,
        readonly=True,
    )
    date_from = fields.Date(
        string='From',
        required=True,
        readonly=True,
    )
    date_to = fields.Date(
        string='To',
        required=True,
        readonly=True,
    )
    csv_file = fields.Binary(
        string='Export CSV',
        readonly=True,
    )
    csv_file_fname = fields.Char(
        string='Stored Filename',
    )
    account_moves = fields.One2many(
        comodel_name='account.move',
        inverse_name='vorlauf_id',
        readonly=False,
    )
    note = fields.Text(
        string='Comment',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    # endregion

    # pylint: disable=copy-wo-api-one,method-required-super
    def copy(self, default=None):
        """
        Prevent copies.
        """
        raise exceptions.UserError(_(
            'Copying this model is not permitted.',
        ))

    def generate_csv_move_lines(
        self,
        move,
        buchungserror,
        errorcount,
        thislog,
        thismovename,
        export_method,
        partnererror,
        buchungszeilencount,
        bookingdict
    ):
        """
        Generate the corresponding csv entries for each move.

        :param move: account_move
        :param buchungserror: list of the account_moves with errors
        :param errorcount: number of errors
        :param thislog: logstring wich contains error descriptions or infos
        :param thismovename: Internal name of the move (for error descriptions)
        :param export_method: gross / net
        :param partnererror: List of the partners with errors (eg. missing ustid)
        :param buchungszeilencount: total number of lines written
        :param bookingdict: Dictionary that contains generated Bookinglines and Headers
        """
        return (
            buchungserror,
            errorcount,
            thislog,
            partnererror,
            buchungszeilencount,
            bookingdict,
        )

    def generate_csv(self, ecofi_csv, bookingdict, log):
        """
        Generate the corresponding csv for each move.

        :param ecofi_csv: object for the csv file
        :param bookingdict: Dictionary that contains generated Bookinglines and Headers
        :param log: logstring which contains error descriptions or infos
        """
        return ecofi_csv, log

    def ecofi_buchungen(self, journal_ids, date_from, date_to):  # noqa: C901
        """
        Generate the csv export by the given parameters.

        :param journal_ids:
            list of journalsIDS which should be exported if the value is False
            all exportable journals will be exported
        :param vorlauf_id:
            id of the vorlauf if an existing export should be generated again
        :param date_from:
            date in wich moves should be exported
        :param date_to:
            date in wich moves should be exported
        .. seealso::
            :class:`ecoservice_financeinterface.wizard.export_ecofi_buchungsaetze.export_ecofi`
        """
        partnererror = []
        buchungserror = []
        user = self.env.user

        journalname = ','.join(journal_ids.mapped('name'))

        try:
            export_method = user.company_id.datev_export_method
        # noqa: B902 as unknown now what the initial purpose was
        # TODO: refactor with specific exception
        except Exception:  # noqa: B902
            export_method = 'net'

        account_move_ids = self.env['account.move'].search([
            ('journal_id', 'in', journal_ids.ids),
            ('state', '=', 'posted'),
            ('vorlauf_id', '=', False),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ])

        # filter account_moves
        # do not export moves where in jounal is type 'bank'
        # and any account is set to 'suspense_account_id'
        account_moves = self.env['account.move']
        for move in account_move_ids:
            ignore_move = False
            for line in move.line_ids:
                journal = line.journal_id
                if journal.type in ['bank', 'cash']:
                    if line.account_id in [journal.suspense_account_id]:
                        ignore_move = True
            if not ignore_move:
                account_moves |= move

        if not account_moves:
            raise exceptions.UserError(_(
                'There are no non-exported moves in the given period and journals!',
            ))

        vorlaufname = self.env['ir.sequence'].sudo().next_by_code('ecofi.vorlauf')
        vorlauf_id = self.env['ecofi'].create({
            'name': str(vorlaufname),
            'date_from': date_from,
            'date_to': date_to,
            'journale': journalname,
        })

        thislog = _(
            'This export is conducted under the Vorlaufname: {vorlaufname}\n'
            '{sign}\n'
            'Start export\n',
        ).format(
            vorlaufname=vorlaufname,
            sign=90 * '-',
        )
        bookingdictcount = 0
        buchungszeilencount = 0
        errorcount = 0
        bookingdict = {}

        for move in account_moves:
            bookingdict['move_bookings'] = []
            move.write({'vorlauf_id': vorlauf_id.id})
            thismovename = '{name}, {ref}: '.format(
                name=move.name,
                ref=move.ref,
            )
            bookingdictcount += 1

            (
                buchungserror,
                errorcount,
                thislog,
                partnererror,
                buchungszeilencount,
                bookingdict,
                move_tax_lines  # pyright: reportUnusedVariable=false
            ) = self.generate_csv_move_lines(
                move,
                buchungserror,
                errorcount,
                thislog,
                thismovename,
                export_method,
                partnererror,
                buchungszeilencount,
                bookingdict,
            )

            sum_export_lines = Decimal('0.00')
            for move_booking in bookingdict['move_bookings']:
                sum_export_lines += Decimal(move_booking[0].replace(',', '.'))
                bookingdict['buchungen'].append(move_booking)

        output = io.StringIO()
        ecofi_csv = csv.writer(
            output,
            delimiter=';',
            quotechar='"',
            quoting=csv.QUOTE_ALL,
        )
        self.generate_csv(ecofi_csv, bookingdict, thislog)

        vorlauf_id.write({
            'csv_file': base64.encodebytes(
                str.encode(
                    output.getvalue(),
                    encoding='cp1252',
                    errors='ignore',
                ),
            ),
            'csv_file_fname': '{}.csv'.format(
                vorlaufname,
            )
        })
        output.close()

        return vorlauf_id
