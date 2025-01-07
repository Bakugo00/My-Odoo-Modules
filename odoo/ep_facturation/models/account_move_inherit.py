from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from num2words import num2words


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    contact_id = fields.Many2one('res.partner', string='Contact', tracking=True)
    amount_text = fields.Text(string="Montant en lettre", compute='_compute_amount', store=True)

    customer_name = fields.Char(string="Nom", tracking=True)
    customer_address = fields.Char(string="Adresse", tracking=True)
    recovery_step_id = fields.Many2one('recovery.step', string='Etape de Recouvrement', tracking=True)

    # invoice_payment_term_id = fields.Many2one('account.payment.term', string='Conditions de paiement',
    #                                           check_company=True,
    #                                           readonly=True, states={'draft': [('readonly', False)]})


    # Function to calculate linear discount from the global discount
    # @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    # def supply_rate(self):
    #     for inv in self:
    #         if inv.discount_type == 'percent':
    #             for line in inv.line_ids:
    #                 line.discount = inv.discount_rate
    #                 line._onchange_price_subtotal()
    #         if inv.discount_type == 'amount':
    #             total = discount = 0.0
    #             for line in inv.invoice_line_ids:
    #                 total += (line.quantity * line.price_unit)
    #             if inv.discount_rate != 0:
    #                 discount = (inv.discount_rate / total) * 100
    #             else:
    #                 discount = inv.discount_rate
    #             for line in inv.line_ids:
    #                 line.discount = discount
    #                 line._onchange_price_subtotal()

    #         inv._compute_invoice_taxes_by_group()

    # ----------  Calculate the stamp  --------------
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        super(AccountMoveInherit,self)._compute_amount()
        for move in self:
            # total_untaxed, total_untaxed_currency = 0.0, 0.0
            # total_tax, total_tax_currency = 0.0, 0.0
            # total_residual, total_residual_currency = 0.0, 0.0
            # total, total_currency = 0.0, 0.0
            # amount_timbre = 0.0
            # for line in move.line_ids:
            #     if move.is_invoice(True):
            #         # === Invoices ===
            #         if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
            #             # Tax amount.
            #             total_tax += line.balance
            #             total_tax_currency += line.amount_currency
            #             total += line.balance
            #             total_currency += line.amount_currency
            #         elif line.istimbre:
            #             # amount & total amount timbre.
            #             amount_timbre += line.amount_currency
            #             # total_untaxed += line.balance
            #             # total_untaxed_currency += line.amount_currency
            #             total += line.balance
            #             total_currency += line.amount_currency
            #         elif line.display_type in ('product', 'rounding'):
            #             # Untaxed amount.
            #             total_untaxed += line.balance
            #             total_untaxed_currency += line.amount_currency
            #             total += line.balance
            #             total_currency += line.amount_currency
            #         elif line.display_type == 'payment_term':
            #             # Residual amount.
            #             total_residual += line.amount_residual
            #             total_residual_currency += line.amount_residual_currency
            #     else:
            #         # === Miscellaneous journal entry ===
            #         if line.debit:
            #             total += line.balance
            #             total_currency += line.amount_currency

            # sign = move.direction_sign


            # move.amount_untaxed = sign * total_untaxed_currency
            # move.amount_tax = sign * total_tax_currency
            # move.amount_total = sign * total_currency
            # move.amount_residual = -sign * total_residual_currency
            # move.amount_untaxed_signed = -total_untaxed
            # move.amount_tax_signed = -total_tax
            # move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            # move.amount_residual_signed = total_residual
            # move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
            # # The amount timbre
            # move.timbre = abs(amount_timbre)

            # Calculate the amount_text value
            move.amount_text = move.currency_id and move.currency_id.amount_to_text(move.amount_total) or ''



    # @api.onchange('invoice_payment_term_id')
    # def onchange_payment_term_id(self):
    #     # if not self.invoice_line_ids:
    #     #     raise ValidationError("Veuillez préciser les lignes de la facture !")
    #     self.payment_type = self.invoice_payment_term_id.payment_type if self.invoice_payment_term_id else False

    # payment_type = fields.Char('Type de paiement')
    # timbre = fields.Monetary(string='Timbre', store=True, readonly=True, track_visibility='onchange')
    # amount_timbre = fields.Monetary(string='Total avec Timbre', store=True, track_visibility='onchange')

    # def _recompute_payment_terms_lines(self):
    #     ''' Compute the dynamic payment term lines of the journal entry.'''
    #     self.ensure_one()
    #     self = self.with_company(self.company_id)
    #     in_draft_mode = self != self._origin
    #     today = fields.Date.context_today(self)
    #     self = self.with_company(self.journal_id.company_id)

    #     def _get_payment_terms_computation_date(self):
    #         ''' Get the date from invoice that will be used to compute the payment terms.
    #         :param self:    The current account.move record.
    #         :return:        A datetime.date object.
    #         '''
    #         if self.invoice_payment_term_id:
    #             return self.invoice_date or today
    #         else:
    #             return self.invoice_date_due or self.invoice_date or today

    #     def _get_timbre_account(self):
    #         ''' Get the account from timbre configuration pannel.
    #         :param self:                    The current account.move record.
    #         :return:                        An account.account record.
    #         '''

    #         # Search new account.
    #         domain = [
    #             ('name', '=', self.env.ref("ep_facturation.config_timbre").name),
    #         ]
    #         # domain = [
    #         #     ('name', '=', 'Calcul Timbre'),
    #         # ]
    #         timbre_account = self.env['config.timbre'].search(domain).account_id
    #         timbre_account_purchase = self.env['config.timbre'].search(domain).account_id_purchase
    #         if self.move_type in ('in_invoice', 'in_refund'):
    #             timbre_account = timbre_account_purchase
    #         if not timbre_account and self.invoice_payment_term_id.payment_type == 'cash':
    #             raise ValidationError(
    #                 "Compte De Droit d’enregistrement n'est pas paramétré. \n Allez dans Facturation/Configuration/Configuration Timbre")
    #         return timbre_account

    #     def _get_payment_terms_account(self, payment_terms_lines):
    #         ''' Get the account from invoice that will be set as receivable / payable account.
    #         :param self:                    The current account.move record.
    #         :param payment_terms_lines:     The current payment terms lines.
    #         :return:                        An account.account record.
    #         '''
    #         if payment_terms_lines:
    #             if self.invoice_payment_term_id.name == 'Espèce (Timbre)':
    #             # if self.invoice_payment_term_id.name == self.env.ref("ep_facturation.account_payment_term_cash").name:
    #                 return _get_timbre_account(self)
    #             # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
    #             else:
    #                 return payment_terms_lines[0].account_id
    #         elif self.partner_id:
    #             # Retrieve account from partner.
    #             if self.is_sale_document(include_receipts=True):
    #                 return self.partner_id.property_account_receivable_id
    #             else:
    #                 return self.partner_id.property_account_payable_id
    #         else:
    #             # Search new account.
    #             domain = [
    #                 ('company_id', '=', self.company_id.id),
    #                 ('internal_type', '=',
    #                  'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
    #             ]
    #             return self.env['account.account'].search(domain, limit=1)

    #     def _compute_timbre(self, total_balance):
    #         today_date = fields.Date.context_today(self)
    #         result = []
    #         amount_timbre = abs(total_balance)
    #         # amount_timbre = total_balance
    #         if self.invoice_payment_term_id and self.invoice_payment_term_id.payment_type == 'cash':
    #             timbre = self.env['config.timbre']._timbre(amount_timbre)
    #             amount_timbre = timbre['timbre'] if self.move_type in ('out_invoice') else -timbre['timbre']
    #             amount_timbre_total = timbre['amount_timbre'] if self.move_type in ('in_invoice') else - timbre[
    #                 'amount_timbre']
    #         result.append((today_date, amount_timbre_total, amount_timbre))
    #         return result

    #     def _compute_payment_terms(self, date, total_balance, total_amount_currency):
    #         ''' Compute the payment terms.
    #         :param self:                    The current account.move record.
    #         :param date:                    The date computed by '_get_payment_terms_computation_date'.
    #         :param total_balance:           The invoice's total in company's currency.
    #         :param total_amount_currency:   The invoice's total in invoice's currency.
    #         :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
    #         '''
    #         if self.invoice_payment_term_id:
    #             to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date,
    #                                                               currency=self.company_id.currency_id)
    #             if self.currency_id == self.company_id.currency_id:
    #                 # Single-currency.
    #                 return [(b[0], b[1], b[1]) for b in to_compute]
    #             else:
    #                 # Multi-currencies.
    #                 to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date,
    #                                                                            currency=self.currency_id)
    #                 return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
    #         else:
    #             return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

    #     def date_maturity(self, existing_terms_lines, account, to_compute, to_timbre):
    #         ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
    #         :param self:                    The current account.move record.
    #         :param existing_terms_lines:    The current payment terms lines.
    #         :param account:                 The account.account record returned by '_get_payment_terms_account'.
    #         :param to_compute:              The list returned by '_compute_payment_terms'.
    #         '''
    #         # As we try to update existing lines, sort them by due date.
    #         existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
    #         existing_terms_lines_index = 0

    #         # Recompute amls: update existing line or create new one for each payment term.
    #         new_terms_lines = self.env['account.move.line']
    #         i = 0
    #         for date_maturity, balance, amount_currency in to_compute:
    #             currency = self.journal_id.company_id.currency_id
    #             if currency and currency.is_zero(balance) and len(to_compute) > 1:
    #                 continue
    #             # if self.invoice_payment_term_id.name != 'Espèce (Timbre)':
    #             if self.invoice_payment_term_id.name != self.env.ref("ep_facturation.account_payment_term_cash").name:
    #                 if existing_terms_lines_index < len(existing_terms_lines):
    #                     # Update existing line.
    #                     candidate = existing_terms_lines[existing_terms_lines_index]
    #                     existing_terms_lines_index += 1
    #                     candidate.update({
    #                         'date_maturity': date_maturity,
    #                         'amount_currency': -amount_currency,
    #                         'debit': balance < 0.0 and -balance or 0.0,
    #                         'credit': balance > 0.0 and balance or 0.0,
    #                     })
    #                 else:
    #                     # Create new line.
    #                     create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
    #                         'account.move.line'].create
    #                     candidate = create_method({
    #                         'name': self.payment_reference or '',
    #                         'debit': balance < 0.0 and -balance or 0.0,
    #                         'credit': balance > 0.0 and balance or 0.0,
    #                         'quantity': 1.0,
    #                         'amount_currency': -amount_currency,
    #                         'date_maturity': date_maturity,
    #                         'move_id': self.id,
    #                         'currency_id': self.currency_id.id,
    #                         'account_id': account.id,
    #                         'partner_id': self.commercial_partner_id.id,
    #                         'exclude_from_invoice_tab': True,
    #                     })
    #                 new_terms_lines += candidate

    #                 if in_draft_mode:
    #                     candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
    #             else:
    #                 for date_maturity, amount_timbre_total, amount_timbre in to_timbre:
    #                     for i in range(2):
    #                         if i == 0:
    #                             candidate = existing_terms_lines[0]
    #                             # candidate = self.env['account.move.line']
    #                             # existing_terms_lines_index += 1
    #                             # candidate = {}
    #                             candidate.update({
    #                                 'name': '',
    #                                 'date_maturity': date_maturity,
    #                                 'amount_currency': -amount_timbre_total,
    #                                 'debit': amount_timbre_total < 0.0 and -amount_timbre_total or 0.0,
    #                                 'credit': amount_timbre_total > 0.0 and amount_timbre_total or 0.0,
    #                             })
    #                         else:
    #                             create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
    #                                 'account.move.line'].create
    #                             candidate2 = create_method({
    #                                 'name': 'Timbre',
    #                                 'debit': amount_timbre < 0.0 and -amount_timbre or 0.0,
    #                                 'credit': amount_timbre > 0.0 and amount_timbre or 0.0,
    #                                 'quantity': 1.0,
    #                                 'amount_currency': -amount_timbre,
    #                                 'move_id': self.id,
    #                                 'currency_id': self.currency_id.id,
    #                                 'account_id': account.id,
    #                                 'partner_id': self.commercial_partner_id.id,
    #                                 'exclude_from_invoice_tab': True,
    #                                 'istimbre': True,
    #                             })
    #                         # candidate += candidate
    #                     new_terms_lines += candidate2 + candidate
    #                     if in_draft_mode:
    #                         candidate2.update(candidate2._get_fields_onchange_balance(force_computation=True))
    #                         candidate.update(candidate._get_fields_onchange_balance(force_computation=True))

    #             # if in_draft_mode:
    #             #     candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
    #         return new_terms_lines

    #     existing_terms_lines = self.line_ids.filtered(
    #         lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
    #     others_lines = self.line_ids.filtered(
    #         lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
    #     timbre_account_id = _get_timbre_account(self)
    #     timbre_lines = self.line_ids.filtered(lambda line: line.account_id.code == timbre_account_id.code)
    #     company_currency_id = (self.company_id or self.env.company).currency_id
    #     total_balance = sum(
    #         others_lines.filtered(lambda line: line.account_id.code != timbre_account_id.code).mapped(
    #             lambda l: company_currency_id.round(l.balance)))
    #     total_amount_currency = sum(others_lines.mapped('amount_currency'))

    #     # timbre_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id in ('Current Liabilities') )

    #     if not others_lines:
    #         self.line_ids -= existing_terms_lines
    #         return

    #     computation_date = _get_payment_terms_computation_date(self)
    #     account = _get_payment_terms_account(self, existing_terms_lines)
    #     to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
    #     to_timbre = _compute_timbre(self,
    #                                 # total_balance) if self.invoice_payment_term_id.name == 'Espèce (Timbre)' else 0
    #                                 total_balance) if self.invoice_payment_term_id.name == self.env.ref("ep_facturation.account_payment_term_cash").name else 0
    #     new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute, to_timbre)

    #     # Remove old terms lines that are no longer needed.
    #     self.line_ids -= existing_terms_lines - new_terms_lines
    #     self.line_ids -= timbre_lines

    #     if new_terms_lines:
    #         self.payment_reference = new_terms_lines[-1].name or ''
    #         self.invoice_date_due = new_terms_lines[-1].date_maturity

    # ------------------------------------------------------------------------

    # def action_post(self):
    #     res = super(AccountMoveInherit, self).action_post()
    #     for invoice in self:
    #         info = ""
    #         if invoice.partner_id:
    #             if invoice.partner_id.company_type == 'company':
    #                 if not invoice.partner_id.rc:
    #                     info += "\n" + " - Registre de commerce " + "\n"
    #                 if not invoice.partner_id.nif:
    #                     info += " - N° Id.Fiscal" + "\n"
    #                 if not invoice.partner_id.nis:
    #                     info += " - N° Id.Statistique" + "\n"
    #                 if not invoice.partner_id.ai:
    #                     info += " - Article d\'imposition" + "\n"
    #
    #                 message = _(
    #                     'Veuillez compléter les informations suivantes du client pour pouvoir confirmer la facture : %s') % \
    #                           info
    #
    #                 if not (invoice.partner_id.rc and invoice.partner_id.nif
    #                         and invoice.partner_id.nis and invoice.partner_id.ai):
    #                     raise ValidationError(message)
    #
    #     return res

    # Used only to fix invoice_partner_display_info field for the migrated database
    # def _compute_invoice_partner_display_info_cron(self):
    #     account_move = self.env['account.move'].search([])
    #     account_move._compute_invoice_partner_display_info()

    # @api.onchange('invoice_line_ids')
    # def _onchange_invoice_line_ids(self):
    #     # res = super(AccountMoveInherit, self)._onchange_invoice_line_ids()
    #     current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
    #     others_lines = self.line_ids - current_invoice_lines
    #     if others_lines and current_invoice_lines - self.invoice_line_ids:
    #         others_lines[0].recompute_tax_line = True
    #     self.line_ids = others_lines + self.invoice_line_ids
    #     print("self.line_ids", self.line_ids)
    #     # self.line_ids += self.stamp_move_line_get()
    #     # stamp_line = self.env["account.move.line"].sudo().create(vals)
    #     self._onchange_recompute_dynamic_lines()


    def _copy_message_to_contact(self, body, **kwargs):
        # Check if there is a contact linked to the invoice
        if self.partner_id:
            if 'message_type' in kwargs:
                message_type = kwargs.get('message_type')
                if message_type == "comment":
                        # Add invoice name in bold to the body
                    formatted_body = f"<b>{self.display_name}</b> <br>{body}"
                        # Copy the formatted message to the linked contact chatter
                    self.partner_id.message_post(body=formatted_body, **kwargs)

    @api.model
    def message_post(self, body='', **kwargs):
        # Call the original message_post method
        result = super(AccountMoveInherit, self).message_post(body=body, **kwargs)
        
        # Copy the message to the linked contact chatter with invoice number in bold
        self._copy_message_to_contact(body, **kwargs)

        return result
