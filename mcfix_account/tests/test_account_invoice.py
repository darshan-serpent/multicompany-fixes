# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account.tests.account_test_users import AccountTestUsers
from odoo.exceptions import ValidationError


class TestAccountInvoiceMC(AccountTestUsers):

    def setUp(self):
        super(TestAccountInvoiceMC, self).setUp()
        self.res_users_model = self.env['res.users']
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']

        # Company
        self.company = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })

        self.cash_journal = self._create_journal(self.company)

        self.pricelist_1 = self._create_pricelist(self.company)
        self.pricelist_2 = self._create_pricelist(self.company_2)

        self.tax_1 = self._create_tax(self.company)
        self.tax_2 = self._create_tax(self.company_2)

        self.fiscal_position_1 = self._create_fiscal_position(self.company)
        self.fiscal_position_2 = self._create_fiscal_position(self.company_2)

        self.payment_term_1 = self._create_payment_terms(self.company)
        self.payment_term_2 = self._create_payment_terms(self.company_2)

        self.account_invoice = self._create_account_invoice(self.company)

    def _create_journal(self, company):
        # Create a cash account
        user_type = self.env.ref('account.data_account_type_liquidity')
        self.cash_account_id = self.account_model.create({
            'name': 'Cash 1 - Test',
            'code': 'test_cash_1',
            'user_type_id': user_type.id,
            'company_id': company.id,
        })

        # Create a journal for cash account
        cash_journal = self.journal_model.create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash_1',
            'type': 'cash',
            'company_id': company.id,
            'default_debit_account_id': self.cash_account_id.id,
            'default_credit_account_id': self.cash_account_id.id,
        })
        return cash_journal

    def _create_pricelist(self, company):
        pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'company_id': company.id,
        })
        return pricelist

    def _create_tax(self, company):
        tax = self.env['account.tax'].create({
            'name': 'Test Tax',
            'company_id': company.id,
            'amount': 3.3,
        })
        return tax

    def _create_fiscal_position(self, company):
        fiscal_position = self.env['account.fiscal.position'].create({
            'name': 'Test Fiscal Position',
            'company_id': company.id,
        })
        return fiscal_position

    def _create_payment_terms(self, company):
        terms = self.env['account.payment.term'].create({
            'name': 'Test payment Terms',
            'company_id': company.id,
        })
        return terms

    def _create_account_invoice(self, company):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.main_partner.id,
            'company_id': company.id,
            'fiscal_position_id': self.fiscal_position_1.id,
            'payment_term_id': self.payment_term_1.id,
            'journal_id': self.cash_journal.id
        })
        return invoice

    def test_invoice_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(ValidationError):
            self.account_invoice.\
                write({'fiscal_position_id': self.fiscal_position_2.id})
        with self.assertRaises(ValidationError):
            self.account_invoice.\
                write({'payment_term_id': self.payment_term_2.id})
        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'company_id': self.company_2.id})
        with self.assertRaises(ValidationError):
            self.account_invoice.\
                write({'journal_id': self.cash_journal.id})
