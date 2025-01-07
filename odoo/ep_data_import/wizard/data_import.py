import base64
import csv
import io
from datetime import datetime
from odoo import fields, models, _
from odoo.tests import Form


class DataImport(models.TransientModel):
    _name = 'data.import'
    _description = 'Importation des données'

    def read_file(self, file):
        csv_data = base64.b64decode(file)
        # data_file = io.StringIO(csv_data.decode("iso-8859-1"))
        data_file = io.StringIO(csv_data.decode("UTF-8"))
        data_file.seek(0)
        csv_reader = csv.DictReader(data_file, delimiter=';')
        return csv_reader

    invoice_attachment = fields.Binary(string="Fichier Facture")
    invoice_store_fname = fields.Char(string="Fichier Facture")

    invoice_line_attachment = fields.Binary(string="Fichier lignes de facture")
    invoice_line_store_fname = fields.Char(string="Fichier lignes de facture")

    payment_attachment = fields.Binary(string="Fichier Paiment")
    payment_store_fname = fields.Char(string="Fichier Paiment")

    refund_attachment = fields.Binary(string="Fichier facture Avoir")
    refund_store_fname = fields.Char(string="Fichier facture Avoir")

    refund_line_attachment = fields.Binary(string="Fichier lignes de facture Avoir")
    refund_line_store_fname = fields.Char(string="Fichier lignes de facture Avoir")

    def invoice_import(self):
        csv_reader = self.read_file(self.invoice_attachment)
        file_reader = []
        file_reader.extend(csv_reader)
        AccountMove = self.env['account.move']

        # %Y-%m-%d
        for row in file_reader:
            old_move_id = row.get("id", "") if "id" in row else ""
            move_name = row.get("name", "") if "name" in row else ""
            invoice_date = datetime.strptime(row.get("date", ""), '%Y-%m-%d') if "date" in row else ""
            date = datetime.strptime(row.get("date", ""), '%Y-%m-%d') if "date" in row else ""
            invoice_date_due = datetime.strptime(row.get("payment_deadline", ""),
                                                 '%Y-%m-%d') if "payment_deadline" in row else ""
            recovery_step_id = row.get("negotiation_step", "") if "negotiation_step" in row else ""
            move_type = 'out_invoice'
            # create_uid = row.get("created_by", "") + max_user_id if "created_by" in row else ""
            create_uid = row.get("created_by", "") if "created_by" in row else ""
            journal_id = 1
            company_id = 1
            currency_id = 114

            # partner_id = row.get("company_id", "") + max_partner_id_2 if "company_id" in row else False
            partner_id = row.get("company_id", "") if "company_id" in row else ""
            contact_id = row.get("contact_id", "") if "contact_id" in row else ""
            payment_state = row.get("payed", "") if "payed" in row else ""
            invoice_user_id = row.get("created_by", "") if "created_by" in row else ""
            quotation_id = row.get("quotation_id", "") if "quotation_id" in row else ""

            # try:
            #     # '%Y-%m-%d'
            #     date_order = datetime.strptime(date_order, '%Y-%m-%d') if date_order != "" else datetime.strptime(create_order, '%Y-%m-%d')
            # except:
            #     date_order = datetime.strptime(create_order, '%Y-%m-%d') if create_order != "" else False

            customer = self.env['res.partner'].sudo().search([('id', '=', int(partner_id))])
            # move = self.env['account.move'].sudo().search([('old_move_id', '=', int(old_move_id))])
            # if move:
            #     move.partner_id = customer.id
            #     move.invoice_partner_display_name = customer.name
            #     print("move,customer : ", move, customer.name)

            account_move_id = AccountMove.sudo().create({
                'quotation_id': quotation_id,
                'old_move_id': old_move_id,
                'posted': True,
                'ref': move_name,
                'name': move_name,
                'invoice_date': invoice_date,
                'date': date,
                'invoice_date_due': invoice_date_due,
                'recovery_step_id': int(recovery_step_id) if recovery_step_id.isnumeric() else False,
                'state': 'draft',
                'move_type': move_type,
                'journal_id': journal_id,
                # 'payment_state': payment_state,
                'partner_id': customer.id if customer else False,
                'contact_id': int(contact_id) if contact_id.isnumeric() else False,
                'invoice_user_id': int(invoice_user_id) if invoice_user_id.isnumeric() else False,
            })
            print("Invoice Created", account_move_id)

    def invoice_line_import(self):
        csv_reader = self.read_file(self.invoice_line_attachment)
        file_reader = []
        file_reader.extend(csv_reader)

        tax_19 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 19)], limit=1)
        tax_17 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 17)], limit=1)
        tax_20 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 20)], limit=1)
        tax_0 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 0)], limit=1)
        name = ""

        for row in file_reader:
            quotation_id = row.get("quotation_id", "") if "quotation_id" in row else ""

            if not quotation_id.isnumeric():
                name = str(name) + "\n" + str(quotation_id)

                if quotation_id == "fin" and move_id:

                    account_move_line = self.env['account.move.line'].sudo().with_context(
                        check_move_validity=False).create({
                        'move_id': move_id.id,
                        'product_id': product_id,
                        'name': str(name),
                        'price_unit': float(price_unit),
                        'quantity': float(quantity),
                        'discount': float(discount),
                        'company_id': 1,
                        'currency_id': 114,
                        'company_currency_id': 114,
                        'tax_ids': [(6, 0, [tax_id.id])],
                        'product_uom_id': 1,
                        'account_id': account_id.id,
                        'exclude_from_invoice_tab': False
                    })
                    print("Invoice Line Created for Invoice ", account_move_line, move_id)
                    if account_move_line:
                        self.add_relation_quotation_invoice(old_sale_order_line_id, account_move_line)
            else:
                if name != "" and move_id:
                    account_move_line = self.env['account.move.line'].sudo().with_context(
                        check_move_validity=False).create({
                        'move_id': move_id.id,
                        'product_id': product_id,
                        # 'product_id': product.id if product else False,
                        'name': str(name),
                        'price_unit': float(price_unit),
                        'quantity': float(quantity),
                        'discount': float(discount),
                        'company_id': self.env.company.id,
                        'currency_id': self.env.company.currency_id.id,
                        # 'company_currency_id': 114,
                        'tax_ids': [(6, 0, [tax_id.id])],
                        'product_uom_id': 1,
                        'account_id': account_id.id,
                        'exclude_from_invoice_tab': False
                    })
                    print("Invoice Line Created for Invoice ", account_move_line, move_id)
                    if account_move_line:
                        self.add_relation_quotation_invoice(old_sale_order_line_id, account_move_line)

                old_sale_order_line_id = row.get("id", "") if "id" in row else ""
                name = row.get("description", "") if "description" in row else ""

                product_id = row.get("product_id", "") if "product_id" in row else ""
                price_unit = row.get("price_unit", "") if "price_unit" in row else ""
                quantity = row.get("quantity", "") if "quantity" in row else ""
                discount = row.get("remise", "") if "remise" in row else ""
                discount_amount = row.get("remise_ammount", "") if "remise_ammount" in row else ""
                discount_type = row.get("remise_type", "") if "remise_type" in row else ""

                move_id = self.env['account.move'].sudo().search([('quotation_id', '=', int(quotation_id))], limit=1)
                # product = self.env['product.product'].sudo().search([('id', '=', product_id)], limit=1)
                account_id = self.env['account.account'].search([('code', '=', 700100)], limit=1)

                tva = row.get("tva", "") if "tva" in row else ""
                tax_id = tax_0

                if tva == '17':
                    tax_id = tax_17
                if tva == '19':
                    tax_id = tax_19
                if tva == '20':
                    tax_id = tax_20

                if discount_type == 'n':
                    price_unit = float(price_unit) - float(discount)
                    discount = 0

                print('name 2', name)
                print('price_unit', price_unit)
                print('quotation_id', quotation_id)

        # self.env.cr.commit()

    # def update_invoices(self):
    #     invoices = self.env['account.move'].sudo().search([])
    #     for invoice in invoices:
    #         if invoice.line_ids:
    #             invoice.line_ids.with_context(check_move_validity=False)._onchange_amount_currency()
    #             invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(True, True)
    #             if invoice.posted:
    #                 invoice.action_post()
    #
    #             if invoice.move_type == 'out_refund':
    #                 origin_move_id = self.env['account.move'].sudo().search([('name', '=', invoice.invoice_origin)])
    #                 print("origin_move_id", origin_move_id)
    #
    #                 if origin_move_id and origin_move_id.state == 'posted':
    #                     line_id = origin_move_id.line_ids.filtered(lambda line: line.account_id.code == "411100")
    #
    #                     lines = self.env['account.move.line'].browse(line_id.id)
    #                     lines += invoice.line_ids.filtered(
    #                         lambda line: line.account_id == lines[0].account_id and not line.reconciled)
    #                     lines.reconcile()
    #                     print("lines", lines)
    #
    #             print("Invoice", invoice, "Updated")

    def add_relation_quotation_invoice(self, old_sale_order_line_id, account_move_line):
        sale_order_line = self.env['sale.order.line'].sudo().search([('id', '=', old_sale_order_line_id)])
        sale_order_line.invoice_lines = [(6, 0, [account_move_line.id])]

    def payment_import(self):
        csv_reader = self.read_file(self.payment_attachment)
        file_reader = []
        file_reader.extend(csv_reader)

        for row in file_reader:
            invoice_id = row.get("invoice_id", "") if "invoice_id" in row else ""
            date = row.get("date", "") if "date" in row else ""
            amount = row.get("ammount", "") if "ammount" in row else ""
            bank_id = row.get("bank_id", "") if "bank_id" in row else ""
            payment_method = row.get("payment_method", "") if "payment_method" in row else ""
            number = row.get("number", "") if "number" in row else ""

            move_id = self.env['account.move'].sudo().search([('old_move_id', '=', int(invoice_id))], limit=1)

            if bank_id.isnumeric():
                partner_bank_id = self.env['res.partner'].sudo().search([('id', '=', int(bank_id))])

            account_id = self.env['account.account'].search([('code', '=', 411100)], limit=1)

            print("move_id", move_id)
            print("invoice_id", invoice_id)

            if payment_method == 'espece':
                journal_id = self.env['account.journal'].sudo().browse(6)
            else:
                journal_id = self.env['account.journal'].sudo().browse(7)

            # if move_id and move_id.state == 'posted' and move_id.payment_state != 'reversed':
            #     action_data = move_id.action_register_payment()
            #     action_data['context'] = {'active_model': 'account.move',
            #                               'active_ids': [move_id.id],
            #                               'default_journal_id': journal_id.id,
            #                               'default_payment_date': date,
            #                               'default_amount': amount,
            #                               'default_bank_check_number': number,
            #                               'default_payment_method': payment_method,
            #                             }
            #
            #     # 'default_partner_bank_id': partner_bank_id.id if partner_bank_id else False,
            #     wizard = Form(self.env['account.payment.register'].with_context(action_data['context'])).save()
            #     action = wizard.action_create_payments()
                # move_id.update({'payment_state': 'paid'})
                # self.env.cr.commit()
                # print("Payment", action)

            if move_id and move_id.state == 'posted' and move_id.payment_state != 'reversed':
                vals = {
                    'payment_method': payment_method,
                    'line_ids': move_id.line_ids,
                    'bank_check_number': number,
                    'payment_date': date,
                    'amount': amount,
                    'source_amount': amount,
                    'source_amount_currency': amount,
                    'communication': move_id.ref,
                    'group_payment': True,
                    'currency_id': 114,
                    'source_currency_id': 114,
                    'can_edit_wizard': True,
                    'can_group_payments': False,
                    'payment_method_id': 1,
                    'payment_difference_handling': 'open',
                    'writeoff_label': 'Write-Off',
                    'partner_id': move_id.partner_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    # 'is_reconciled': True,
                    # 'is_matched': False,
                    'journal_id': journal_id.id,
                    # 'destination_account_id': 399,
                    # 'is_internal_transfer': False,
                }

                # if partner_bank_id:
                #     vals[partner_bank_id] = partner_bank_id.id

                # print(vals)

                account_payment_register = self.env['account.payment.register'].sudo().with_context(check_move_validity=False).create(vals)

                res = account_payment_register.with_context(
                skip_account_move_synchronization=True).action_create_payments()
                # print("res", res)

                self.env.cr.commit()

                # account_payment = self.env['account.payment'].sudo().create({
                #     'payment_method': payment_method,
                #     'move_id': move_id.id,
                #     'bank_check_number': number,
                #     'date': date,
                #     'amount': amount,
                #     'ref': move_id.ref,
                #     'partner_id': move_id.partner_id.id,
                #     'payment_type': 'outbound',
                #     'partner_type': 'customer',
                #     'is_reconciled': True,
                #     'is_matched': False,
                #     'journal_id': journal_id,
                #     'destination_account_id': 399,
                #     'partner_bank_id': partner_bank_id.id if partner_bank_id else False,
                #     'is_internal_transfer': False,
                # })
                # print("Payment Created for Invoice ", account_payment, move_id)

    def refund_import(self):
        csv_reader = self.read_file(self.refund_attachment)
        file_reader = []
        file_reader.extend(csv_reader)
        AccountMove = self.env['account.move']

        for row in file_reader:
            old_move_id = row.get("id", "") if "id" in row else ""
            invoice_id = row.get("invoice_id", "") if "invoice_id" in row else ""
            move_name = row.get("name", "") if "name" in row else ""
            invoice_date = datetime.strptime(row.get("date", ""), '%Y-%m-%d') if "date" in row else ""
            date = datetime.strptime(row.get("date", ""), '%Y-%m-%d') if "date" in row else ""
            move_type = 'out_refund'
            create_uid = row.get("created_by", "") if "created_by" in row else ""
            journal_id = 1

            partner_id = row.get("company_id", "") if "company_id" in row else ""
            contact_id = row.get("contact_id", "") if "contact_id" in row else ""
            payment_state = row.get("payed", "") if "payed" in row else ""
            invoice_user_id = row.get("created_by", "") if "created_by" in row else ""

            move_id = self.env['account.move'].sudo().search([('old_move_id', '=', invoice_id)], limit=1)
            customer = self.env['res.partner'].sudo().search([('id', '=', int(partner_id))])

            # refund_move_id = self.env['account.move'].sudo().search([('old_move_id', '=', old_move_id)], limit=1)
            # if refund_move_id and move_id:
            #     refund_move_id.invoice_origin = move_id.name
            #     print("refund_move_id.invoice_origin", refund_move_id , refund_move_id.invoice_origin)

            account_move_id = AccountMove.sudo().create({
                'invoice_origin': move_id.name if move_id else "",
                'old_move_id': old_move_id,
                'ref': move_name,
                'invoice_date': invoice_date,
                'date': date,
                'state': 'draft',
                'move_type': move_type,
                'journal_id': journal_id,
                'partner_id': customer.id if customer else False,
                'contact_id': int(contact_id) if contact_id.isnumeric() else False,
                'invoice_user_id': int(invoice_user_id) if invoice_user_id.isnumeric() else False,
            })
            print("Refund Created", account_move_id)

    def refund_line_import_2(self):
        csv_reader = self.read_file(self.refund_line_attachment)
        file_reader = []
        file_reader.extend(csv_reader)

        tax_19 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 19)], limit=1)
        tax_17 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 17)], limit=1)
        tax_20 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 20)], limit=1)

        AccountMoveLine = self.env['account.move.line']

        for row in file_reader:
            old_sale_order_line_id = row.get("id", "") if "id" in row else ""
            product_id = row.get("product_id", "") if "product_id" in row else ""
            name = row.get("description", "") if "description" in row else ""
            price_unit = row.get("price", "") if "price" in row else ""
            quantity = row.get("quantity", "") if "quantity" in row else ""
            discount = row.get("remise", "") if "remise" in row else ""
            discount_amount = row.get("remise_ammount", "") if "remise_ammount" in row else ""
            discount_type = row.get("remise_type", "") if "remise_type" in row else ""

            credit_note_id = row.get("credit_note_id", "") if "credit_note_id" in row else ""

            move_id = self.env['account.move'].sudo().search([('old_move_id', '=', credit_note_id)], limit=1)
            tax_id = row.get("tva", "") if "tva" in row else ""

            if tax_id == '17':
                tax_id = tax_17
            if tax_id == '19':
                tax_id = tax_19
            if tax_id == '20':
                tax_id = tax_20

            if discount_type == 'n':
                discount = 0
                price_unit = float(price_unit) - discount

            print('tax_id', tax_id)

            account_move_line = AccountMoveLine.sudo().create({
                'move_id': move_id.id,
                'product_id': product_id,
                'name': name,
                'price_unit': float(price_unit),
                'quantity': float(quantity),
                'discount': float(discount),
                'tax_ids': [(6, 0, [tax_id.id])],
                'product_uom_id': 1,
                'account_id': 813,
                'exclude_from_invoice_tab': False
            })
            print("Refund Line Created for Refund ", account_move_line, move_id)

    def refund_line_import(self):
        csv_reader = self.read_file(self.refund_line_attachment)
        file_reader = []
        file_reader.extend(csv_reader)

        tax_19 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 19)], limit=1)
        tax_17 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 17)], limit=1)
        tax_20 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 20)], limit=1)
        tax_0 = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', 0)], limit=1)
        name = ""

        for row in file_reader:
            credit_note_id = row.get("credit_note_id", "") if "credit_note_id" in row else ""

            if not credit_note_id.isnumeric():
                name = str(name) + "\n" + str(credit_note_id)

                if credit_note_id == "fin" and move_id:
                    account_move_line = self.env['account.move.line'].sudo().with_context(
                        check_move_validity=False).create({
                        'move_id': move_id.id,
                        'product_id': product_id,
                        'name': str(name),
                        'price_unit': float(price_unit),
                        'quantity': float(quantity),
                        'discount': float(discount),
                        'company_id': 1,
                        'currency_id': 114,
                        'company_currency_id': 114,
                        'tax_ids': [(6, 0, [tax_id.id])],
                        'product_uom_id': 1,
                        'account_id': account_id.id,
                        'exclude_from_invoice_tab': False
                    })
                    print("Refund Line Created for Refund ", account_move_line, move_id)

            else:
                if name != "" and credit_note_id:
                    account_move_line = self.env['account.move.line'].sudo().with_context(
                        check_move_validity=False).create({
                        'move_id': move_id.id,
                        'product_id': product_id,
                        # 'product_id': product.id if product else False,
                        'name': str(name),
                        'price_unit': float(price_unit),
                        'quantity': float(quantity),
                        'discount': float(discount),
                        'company_id': self.env.company.id,
                        'currency_id': self.env.company.currency_id.id,
                        # 'company_currency_id': 114,
                        'tax_ids': [(6, 0, [tax_id.id])],
                        'product_uom_id': 1,
                        'account_id': account_id.id,
                        'exclude_from_invoice_tab': False
                    })
                    print("Refund Line Created for Refund ", account_move_line, move_id)

                name = row.get("description", "") if "description" in row else ""
                product_id = row.get("product_id", "") if "product_id" in row else ""
                price_unit = row.get("price_unit", "") if "price_unit" in row else ""
                quantity = row.get("quantity", "") if "quantity" in row else ""
                discount = row.get("remise", "") if "remise" in row else ""
                discount_amount = row.get("remise_ammount", "") if "remise_ammount" in row else ""
                discount_type = row.get("remise_type", "") if "remise_type" in row else ""

                account_id = self.env['account.account'].search([('code', '=', 700100)], limit=1)

                credit_note_id = row.get("credit_note_id", "") if "credit_note_id" in row else ""
                move_id = self.env['account.move'].sudo().search([('old_move_id', '=', credit_note_id)], limit=1)

                tva = row.get("tva", "") if "tva" in row else ""
                tax_id = tax_0

                if tva == '17':
                    tax_id = tax_17
                if tva == '19':
                    tax_id = tax_19
                if tva == '20':
                    tax_id = tax_20

                if discount_type == 'n':
                    price_unit = float(price_unit) - float(discount)
                    discount = 0

        # self.env.cr.commit()

    def update_invoices(self):
        invoices = self.env['account.move'].sudo().search([('move_type', '=', 'out_invoice'), ('state', '=', 'draft'),
                                                           ('amount_total', '>=', 0)], order='invoice_date')
        print(len(invoices))

        for invoice in invoices:
            print("Invoice out invoice", invoice)

            if invoice.line_ids:
                invoice.line_ids.with_context(check_move_validity=False)._onchange_amount_currency()
                invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(True, True)
                invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()

            if invoice.line_ids and invoice.partner_id and invoice.state == 'draft':
                invoice.action_post()

            self.env.cr.commit()

    def update_refunds(self):
        # invoices = self.env['account.move'].sudo().search([('move_type', '=', 'out_refund'), ('state', '=', 'draft')], order='invoice_date')
        invoices = self.env['account.move'].sudo().search([('move_type', '=', 'out_refund')], order='invoice_date')
        print(len(invoices))

        for invoice in invoices:
            print("Invoice out refund", invoice)

            # if invoice.line_ids:
            #     invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
            #     invoice.line_ids.with_context(check_move_validity=False)._onchange_amount_currency()
            #     invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(True, True)

            # if invoice.partner_id and invoice.state == 'draft' and invoice.invoice_line_ids:
            if invoice.partner_id and invoice.invoice_line_ids:
                # invoice.action_post()

                if invoice.invoice_origin != '/':

                    origin_move_id = self.env['account.move'].sudo().search([('name', '=', invoice.invoice_origin)])

                    if origin_move_id:
                        if origin_move_id.state == 'posted':
                            line_id = origin_move_id.line_ids.filtered(lambda line: line.account_id.code == '413000')
                            if not line_id:
                                line_id = origin_move_id.line_ids.filtered(lambda line: line.account_id.code == '411100')
                            lines = self.env['account.move.line'].browse(line_id.id)
                            lines += invoice.line_ids.filtered(
                                lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                            lines.reconcile()
                            origin_move_id.payment_state = "reversed"
                        print("origin_move_id", origin_move_id)
                        # self.env.cr.commit()
                    else:
                        import logging
                        _logger = logging.getLogger(__name__)
                        _logger.warning('Facture negative', invoice, invoice.amount_total)

            self.env.cr.commit()

    # csv_data = fields.Binary()
    # filename = fields.Char()
    #
    # def generate_attachment(self):
    #
    #     # file = open('/usr/lib/python3/dist-packages/odoo/addons_cetic2/EDI.txt', 'r+')
    #     # file = open('c:/myfile.txt', 'r+')
    #     file = open('c:/test__ligne_facture.csv', 'r+')
    #
    #     # file = open('EDI.txt', 'r+')
    #     file_data = file.read()
    #
    #     values = {
    #         'name': "test__ligne_facture.csv",
    #         'store_fname': 'test__ligne_facture.csv',
    #         'res_model': 'sale.order',
    #         'res_id': 19232,
    #         'type': 'binary',
    #         'public': True,
    #         'datas': base64.b64encode(file_data.encode('utf-8')),
    #     }
    #
    #     attachment_id = self.env['ir.attachment'].sudo().create(values)
    #     print("attachment_id", attachment_id)
    #
