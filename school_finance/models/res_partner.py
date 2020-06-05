# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SchoolFinance(models.Model):
    _inherit = 'res.partner'

    family_invoice_ids = fields.Many2many("account.move", compute="_compute_family_invoice_ids", store=True, domain=[('type', '=', 'out_invoice')], context={'default_type': 'out_invoice', 'type': 'out_invoice','tree_view_ref': 'account.view_invoice_tree'})
    invoice_address_id = fields.Many2one("res.partner", string="Invoice Address")
    family_res_finance_ids = fields.One2many("school_finance.financial.res.percent", 'partner_id', string="Family resposability")
    student_invoice_ids = fields.One2many("account.move", "student_id", string="Student Invoices")

    def _check_category_sum(self):
        for record in self:
            categories = [{category.category_id.id:category.percent} for category in record.family_res_finance_ids]
            categories_ids = {category.category_id for category in record.family_res_finance_ids}

            for category_id in categories_ids:
                percent_sum = sum([category.percent for category in record.family_res_finance_ids if category.category_id == category_id])
                if percent_sum != 100:
                    raise UserError(_("Category: {} doesn't sum 100!".format(category_id.complete_name)))

    @api.model
    def create(self, vals):
        try:
            partners = super().create(vals)
            partners._check_category_sum()
            return partners
        except:
            self._cr.rollback()
            raise


    def write(self, vals):
        try:
            partners = super().write(vals)
            self._check_category_sum()
            return partners
        except:
            self._cr.rollback()
            raise
    def _compute_family_invoice_ids(self):
        """
            Calculamos todos los invoices de la familia dependiento de sus miembros
        """
        for record in self:
            invoices = False
            if record.is_company:
                invoices = self.member_ids.invoice_ids + self.member_ids.student_invoice_ids + self.invoice_ids
            record.family_invoice_ids = invoices

class FinacialResponsabilityPercent(models.Model):
    _name = "school_finance.financial.res.percent"
    _description = "Realted model to finance responsabilty"

    partner_id = fields.Many2one("res.partner", string="Customer", domain=[("is_family", "=", False)])
    partner_family_ids = fields.Many2many(related="partner_id.family_ids")

    family_id = fields.Many2one("res.partner", required=True, string="Family")
    category_id = fields.Many2one("product.category", required=True, string="Category", domain=[("parent_id", "=", False)])
    percent = fields.Integer("Percent")

    @api.onchange('family_id')
    def _get_family_domain(self):
        self.ensure_one()
        family_ids = self.partner_id.family_ids.ids
        return  {'domain':{'family_id':[("is_family", "=", True), ("is_company", "=", True), ('id', 'in', family_ids)]}}

    @api.model
    def create(self, vals):
        
        family_id = self.env["res.partner"].browse(vals["family_id"])
        if not family_id.is_family:
            raise ValidationError(_("%s is not a family!") % family_id.display_name)

        return super().create(vals)
