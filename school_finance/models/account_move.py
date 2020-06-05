# -*- coding: utf-8 -*-

from odoo import fields, models

class Invoice(models.Model):
    _inherit = "account.move"

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family", domain=[('is_family', '=', True)])

    family_members_ids = fields.Many2many(related="family_id.member_ids")


class Invoice(models.Model):
    _inherit = "account.journal"

    template_with_payment_id = fields.Many2one("ir.ui.view", string="Template with payment",
                                                 domain=[("type", "=", "qweb")], default=lambda self: self.env.ref('account.report_invoice_document_with_payments'))
    template_id = fields.Many2one("ir.ui.view", string="Template without payment",
                                   domain=[("type", "=", "qweb")], default=lambda self: self.env.ref('account.report_invoice_document'))
