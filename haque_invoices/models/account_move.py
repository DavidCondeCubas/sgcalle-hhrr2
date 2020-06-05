# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class Invoice(models.Model):
    _inherit = "account.move"

    invoice_date_invalid = fields.Date("Invalid Date")
    late_fee_amount = fields.Monetary()

