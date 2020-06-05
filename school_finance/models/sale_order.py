# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrderForStudents(models.Model):
    _inherit = "sale.order"

    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")
    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """

        # If it isn't a student, then we proceed with default behaviour
        no_student_records = self.filtered( lambda record: record.partner_id.person_type != "student")
        student_recods     = self.filtered( lambda record: record.partner_id.person_type == "student")
        invoice_no_students = self.env["account.move"]
        
        if no_student_records:
            invoice_no_students = super(SaleOrderForStudents, no_student_records)._create_invoices(grouped, final)


        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in student_recods:
            pending_section = None

            # Invoice values.
            partner_responsible_categ = {category.category_id for category in order.partner_id.family_res_finance_ids}
            for line in order.order_line:
                product_categs = list()
                parent_category_id = line.product_id.categ_id

                while parent_category_id:
                    if parent_category_id in partner_responsible_categ:
                        break;
                    parent_category_id = parent_category_id.parent_id

                if not parent_category_id:
                    raise UserError(_('There is no responsible family for %s') % (line.product_id.categ_id.name))

            for family_id in self.partner_id.family_ids:
                invoice_vals = order._prepare_invoice()
                invoice_vals["partner_id"] = family_id.invoice_address_id.id
                invoice_vals["student_id"] = order.partner_id.id
                invoice_vals["family_id"] = family_id.id

                # Invoice line values (keep only necessary sections).
                for line in order.order_line:
                    if line.display_type == 'line_section':
                        pending_section = line
                        continue
                    if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                        continue
                    if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                        if pending_section:
                            invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                            pending_section = None

                        product_line = line._prepare_invoice_line()
                        
                        # Skip if we found that family isn't the category's responsible
                        if not family_id in [category.family_id for category in order.partner_id.family_res_finance_ids if category.category_id == parent_category_id]:
                            continue

                        percent_sum = sum([category.percent for category in order.partner_id.family_res_finance_ids if category.category_id == parent_category_id and category.family_id == family_id])
                        percent_sum /= 100

                        product_line["price_unit"] *= percent_sum
                        invoice_vals['invoice_line_ids'].append((0, 0, product_line))

                        # This gave error
                        # product_line["account_id"] = line.product_id.property_account_income_id.id


                if not invoice_vals['invoice_line_ids']:
                    continue
                    # raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

                invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and not invoice_no_students:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # invoice_vals_list.append(invoice_vals_list[0])
        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.

        # moves = self.env['account.move']
        #for invoice in invoice_vals_list:
        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_subscribe(move.family_id.financial_res_ids.ids)
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        all_moves = moves + invoice_no_students

        receivable_behaviour = self.env["ir.config_parameter"].get_param('school_finance.receivable_behaviour')
            

        for order in self:
            if receivable_behaviour == 'student' and order.partner_id.person_type == 'student':
                receivable_lines = order.invoice_ids.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
                receivable_lines.sudo().write({
                    "account_id": order.partner_id.property_account_receivable_id.id
                })

            if order.journal_id:
                order.invoice_ids.write({
                    "journal_id": order.journal_id.id
                })
        
        return all_moves
        
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super().product_uom_change()
        if not self.order_id.pricelist_id and not self.order_id.partner_id:
            self.price_unit = self.product_id.lst_price

    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()

        if not self.order_id.pricelist_id and not self.order_id.partner_id:
            price_unit = self.product_id.lst_price
            self.write({"price_unit": price_unit})
        
        return res
        