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

    invoice_date_due = fields.Date()
    invoice_date_invalid = fields.Date()
    late_fee_amount = fields.Monetary()

    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")
    def _create_invoices(self, grouped=False, final=False):
        all_moves = super()._create_invoices(grouped, final)
        for order in self:
            order.invoice_ids.write({
                "invoice_date_invalid": order.invoice_date_invalid,
                "invoice_date_due": order.invoice_date_due,
                "late_fee_amount": order.late_fee_amount,
            })
        return all_moves
        