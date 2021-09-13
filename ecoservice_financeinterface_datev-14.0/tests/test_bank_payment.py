# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from .base_setup_datev import (
    KEY_ACCOUNT,
    KEY_AMOUNT,
    KEY_BOOKING_KEY,
    KEY_COUNTER,
    KEY_CREDIT_DEBIT,
    BaseSetupDatev,
)


class TestBankPayment(BaseSetupDatev):

    # def test_bank_payment_for_invoice(self):
    #     payment_method = self.env.ref('account.account_payment_method_manual_in')
    #     journal = self.AJ.search(
    #         [
    #             ('type', '=', 'bank'),
    #             ('company_id', '=', self.env.company.id),
    #         ],
    #         limit=1,
    #     )
    #     invoice = self._create_invoice()
    #     expected_lines = [
    #         {
    #             KEY_AMOUNT: '476,00',
    #             KEY_CREDIT_DEBIT: 'H',
    #             KEY_ACCOUNT: '8400',
    #             KEY_COUNTER: '1410',
    #             KEY_BOOKING_KEY: '',
    #         },
    #         {
    #             KEY_AMOUNT: '476,00',
    #             KEY_CREDIT_DEBIT: 'H',
    #             KEY_ACCOUNT: '1410',
    #             KEY_COUNTER: '1203',
    #             KEY_BOOKING_KEY: '',
    #         },
    #         # {
    #         #     KEY_AMOUNT: '476,00',
    #         #     KEY_CREDIT_DEBIT: 'H',
    #         #     KEY_ACCOUNT: '1203',
    #         #     KEY_COUNTER: '1202',
    #         #     KEY_BOOKING_KEY: '',
    #         # }
    #     ]

    #     invoice._post(soft=False)
    #     register_payment = invoice.action_register_payment()
    #     payment = self.AP.with_context(register_payment['context']).create({
    #         'payment_method_id': payment_method.id,
    #         'journal_id': journal.id,
    #         'amount': invoice.amount_total,
    #         'date': invoice.invoice_date,
    #     })
    #     payment.action_post()

    #     actual_lines = list(self._get_csv_reader())

    #     self._test_export_line(expected_lines, actual_lines)

    # Test 8
    # Konfiguration:
    # Buchungszeilen gruppieren: ja
    # Soll und Haben kumulieren: ja
    # Geschäftsfall: Eine Mietzahlung über Bank wird direkt auf das Sachkonto unter Beachtung der Vorsteuer gebucht.  # noqa: E501

    # S 4210 (Sachkonto) an H 1201 (Bankkonto) mit Buchungsschlüssel 9

    def test_direct_bank_payment(self):
        journal = self.AJ.search(
            [
                ('type', '=', 'bank'),
                ('company_id', '=', self.env.company.id),
            ],
            limit=1,
        )

        account_4210 = self.AA.search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', '4210'),
        ])
        account_1576 = self.AA.search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', '1576'),
        ])
        account_1202 = self.AA.search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', '1202'),
        ])

        move = self.AM.create({
            'move_type': 'entry',
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'account_id': account_4210.id,
                    'name': 'Mietzahlung',
                    'debit': 200.00,
                    'credit': 0.00,
                    'tax_ids': [(6, 0, self.tax_vst_19.ids)],
                }),
                (0, 0, {
                    'account_id': account_1576.id,
                    'name': 'Mietzahlung-VSt.19',
                    'debit': 38.00,
                    'credit': 0.00,
                }),
                (0, 0, {
                    'account_id': account_1202.id,
                    'name': 'Mietzahlung',
                    'debit': 0.00,
                    'credit': 238.00,
                })
            ],
        })

        expected_lines = [
            {
                KEY_AMOUNT: '238,00',
                KEY_CREDIT_DEBIT: 'S',
                KEY_ACCOUNT: '4210',
                KEY_COUNTER: '1202',
                KEY_BOOKING_KEY: '9',
            },
        ]

        move._post(soft=False)
        actual_lines = list(self._get_csv_reader())

        self._test_export_line(expected_lines, actual_lines)

    # Test 9
    # Konfiguration:
    # Buchungszeilen gruppieren: ja
    # Soll und Haben kumulieren: ja
    # Geschäftsfall: In die Kasse wird Geld eingezahlt und eine Rechnung für Lebensmittel bezahlt.  # noqa: E501

    # S 1001 Kasse an H 136001 Geldtransfer
    # S 4650 Bewirtungskosten am H 1001 Kasse mit BU 9

    # Auskommentiert da dieser Test neu geschrieben werden muss.

    # def test_cash_booking_bank_payment(self):
    #     journal = self.AJ.search(
    #         [
    #             ('type', '=', 'cash'),
    #             ('company_id', '=', self.env.company.id),
    #         ],
    #         limit=1,
    #     )

    #     account_136001 = self.AA.search([
    #         ('company_id', '=', self.env.company.id),
    #         ('code', '=', '136001'),
    #     ])
    #     account_4650 = self.AA.search([
    #         ('company_id', '=', self.env.company.id),
    #         ('code', '=', '4650'),
    #     ])
    #     account_1576 = self.AA.search([
    #         ('company_id', '=', self.env.company.id),
    #         ('code', '=', '1576'),
    #     ])
    #     account_1001 = self.AA.search([
    #         ('company_id', '=', self.env.company.id),
    #         ('code', '=', '1002'),
    #     ])

    #     move = self.AM.create([
    #         {
    #             'move_type': 'entry',
    #             'journal_id': journal.id,
    #             'line_ids': [
    #                 (0, 0, {
    #                     'account_id': account_136001.id,
    #                     'name': 'Geldeinlage',
    #                     'debit': 0.00,
    #                     'credit': 100.00,
    #                 }),
    #                 (0, 0, {
    #                     'account_id': account_1001.id,
    #                     'name': 'Geldeinlage',
    #                     'debit': 100.00,
    #                     'credit': 0.00,
    #                 }),
    #             ],
    #         },
    #         {
    #             'move_type': 'entry',
    #             'journal_id': journal.id,
    #             'line_ids': [
    #                 (0, 0, {
    #                     'account_id': account_4650.id,
    #                     'name': 'Mietzahlung',
    #                     'debit': 10.00,
    #                     'credit': 0.00,
    #                     'tax_ids': [(6, 0, self.tax_vst_19_price_include.ids)],
    #                 }),
    #                 (0, 0, {
    #                     'account_id': account_1576.id,
    #                     'name': 'Mietzahlung-VSt.19',
    #                     'debit': 1.90,
    #                     'credit': 0.00,
    #                 }),
    #                 (0, 0, {
    #                     'account_id': account_1001.id,
    #                     'name': 'Mietzahlung',
    #                     'debit': 0.00,
    #                     'credit': 11.90,
    #                 })
    #             ],
    #         },
    #     ])

    #     expected_lines = [
    #         {
    #             KEY_AMOUNT: '11,90',
    #             KEY_CREDIT_DEBIT: 'S',
    #             KEY_ACCOUNT: '4650',
    #             KEY_COUNTER: '1002',
    #             KEY_BOOKING_KEY: '9',
    #         },
    #         {
    #             KEY_AMOUNT: '100,00',
    #             KEY_CREDIT_DEBIT: 'H',
    #             KEY_ACCOUNT: '136001',
    #             KEY_COUNTER: '1002',
    #             KEY_BOOKING_KEY: '',
    #         },
    #     ]

    #     move._post(soft=False)
    #     actual_lines = list(self._get_csv_reader())

    #     self._test_export_line(expected_lines, actual_lines)
