from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit = "account.move"


    payment_method = fields.Selection([
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
        ('espece', 'Espèces')],
        string='Méthode de paiement', default='', tracking=True)
    
    amount_timbre = fields.Monetary(string='Montant Timbre',compute='_compute_amount', store=True, track_visibility='onchange')

    def _recompute_stamp_tax_lines(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.payment_method == 'espece' and rec.move_type in type_list:
                # stamp_tax = self.env.ref("ep_stamp_tax.tva_stamp1")
                stamp_tax = self.env['account.tax'].search([('name','=','Timbre 1,0%'),('company_id','=',self.company_id.id)])
                tax = stamp_tax.compute_all(rec.amount_total, currency=rec.currency_id, quantity=1, product=None,
                                                partner=rec.partner_id)['taxes'][0]
                if stamp_tax.min_value > tax['amount']:
                    amount = stamp_tax.min_value
                elif tax['amount'] > stamp_tax.max_value:
                    amount = stamp_tax.max_value
                else:
                    amount = tax['amount'] 
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    name = "Timbre 1,0%"                    
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                    stamp_lines = self.line_ids.filtered(
                        lambda line: line.name and line.name.find('Timbre 1,0%') == 0)
                    if stamp_lines:

                        if(self.move_type == "out_invoice" or self.move_type == "out_refund"):
                            stamp_lines.update({
                                'name': name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'balance': (amount < 0.0 and -amount or 0.0) - (amount > 0.0 and amount or 0.0),
                            })
                        if (self.move_type == "in_invoice" or self.move_type == "in_refund"):
                            stamp_lines.update({
                                'name': name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'balance': (amount > 0.0 and amount or 0.0) - (amount < 0.0 and -amount or 0.0) ,
                            })
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or \
                                        self.env['account.move.line'].create

                        if  (self.move_type == "out_invoice"
                                     or self.move_type == "out_refund"):
                            dict = {
                                'move_name': self.name,
                                'display_type': 'tax',
                                'name': name,
                                'price_unit': amount,
                                'quantity': 1,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'account_id': tax['account_id'],
                                'tax_line_id': tax['id'],
                                'tax_ids': [(4, stamp_tax.id)],
                                'tax_repartition_line_id': tax['tax_repartition_line_id'],
                                'move_id': self._origin,
                                'date': self.date,
                                # 'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'currency_id': self.company_id.currency_id.id,
                            }
                            if self.move_type == "out_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                    'balance': (amount < 0.0 and -amount or 0.0) - (amount > 0.0 and amount or 0.0),
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                    'balance': (amount > 0.0 and amount or 0.0) - (amount < 0.0 and -amount or 0.0) ,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Timbre 1,0%') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                self.line_ids = [(0, 0, dict)]
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Timbre 1,0%') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id

                        if (self.move_type == "in_invoice"
                                     or self.move_type == "in_refund"):
                            dict = {
                                'move_name': self.name,
                                'display_type': 'tax',
                                'name': name,
                                'price_unit':amount,
                                'quantity': 1,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'account_id': tax['account_id'],
                                'tax_line_id': tax['id'],
                                'tax_ids': [(4, stamp_tax.id)],
                                'tax_repartition_line_id': tax['tax_repartition_line_id'],
                                'move_id': self.id,
                                'date': self.date,
                                # 'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'currency_id': self.company_id.currency_id.id,
                            }

                            if self.move_type == "in_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            self.line_ids += create_method(dict)

                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type not in ('asset_receivable', 'liability_payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                            'amount_currency': -total_amount_currency,
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        })
                    else:
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                        stamp_lines = self.line_ids.filtered(
                            lambda line: line.name and line.name.find('Timbre 1,0%') == 0)
                        other_lines = self.line_ids - terms_lines - stamp_lines
                        total_balance = sum(other_lines.mapped('balance')) - amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        }
                        dict2 = {
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        }
                        self.line_ids = [(1, stamp_lines.id, dict1), (1, terms_lines.id, dict2)]

            elif rec.payment_method != 'espece':
                stamp_lines = rec.line_ids.filtered(
                    lambda line: line.name and line.name.find('Timbre 1,0%') == 0)
                if stamp_lines:
                    terms_lines =  rec.line_ids.filtered(
                    lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                    other_lines = rec.line_ids - terms_lines - stamp_lines
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                        'balance': (total_balance < 0.0 and -total_balance or 0.0) - (total_balance > 0.0 and total_balance or 0.0),
                    })
                    rec.line_ids -= stamp_lines
                    stamp_lines.with_context(dynamic_unlink=True).unlink()


    def _compute_tax_totals(self):
        super(AccountMoveInherit, self)._compute_tax_totals()
        self._recompute_stamp_tax_lines()


    @api.model
    def create(self, values):
    # Create the record
        record = super(AccountMoveInherit, self).create(values)
        # Compute stamp tax if payment method is 'espece'
        if values.get('payment_method') == 'espece':
            record._recompute_stamp_tax_lines()
        return record

    def write(self, values):
    # Update the record
        res = super(AccountMoveInherit, self).write(values)
        # Check if payment_method is being updated
        if 'payment_method' in values:
            # Compute stamp tax if payment method is 'espece'
            if values.get('payment_method') == 'espece':
                self._recompute_stamp_tax_lines()
            else:
                # If payment method is not 'espece', remove stamp tax lines
                self.line_ids.filtered(lambda line: line.name and line.name.find('Timbre 1,0%') == 0).with_context(dynamic_unlink=True).unlink()
        return res



    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_amount(self):
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_stamp_tax, total_stamp_tax_currency = 0.0, 0.0 #add the stamp calculation
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0

            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        if line.tax_line_id.is_stamp: # test if the tax is stamp tax
                            total_stamp_tax += line.balance
                            total_stamp_tax_currency += line.amount_currency
                        else:
                            total_tax += line.balance
                            total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            sign = move.direction_sign 
            move.amount_timbre = abs(total_stamp_tax_currency)
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)

     
    def action_post(self):
        for invoice in self:
            if invoice.move_type == 'out_invoice' and not invoice.payment_method:
                message = _(
                    'Veuillez spécifier la méthode de paiment pour pouvoir confirmer la facture ') 
                raise ValidationError(message)
        return super(AccountMoveInherit,self).action_post()
    
    def action_register_payment(self):
        action = super(AccountMoveInherit,self).action_register_payment()
        payment_meth = set(self.mapped('payment_method'))
        if len(payment_meth) != 1:
            raise ValidationError('Veuillez spécifier une seule méthode de paiment pour toutes les factures selectionnées!')
        action["context"].update(
            {
                "default_payment_method": self[0].payment_method,
            }
        )
        return action