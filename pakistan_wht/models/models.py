# -*- coding: utf-8 -*-

from odoo import models, fields, api

wht_dict = [
    ('filler', 'Filler'),
    ('no_filler', 'No filler'),
    ('exempt', 'Exempt'),
]


class TaxRates(models.Model):
    _name = 'pakistan_wht.tax_rate'
    _description = 'Pakistan withholding taxes rate'

    tax_category_id = fields.Many2one("pakistan_wht.tax_category", string="Tax category", required=True)
    company_id = fields.Many2one("res.company", required=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    status = fields.Selection(wht_dict, required=True, string='Status')

    exempt_upto = fields.Monetary(string='Yearly - Exempt upto')
    tax_rate = fields.Float(string='Tax rate', digits=(6, 3))
    tax_id = fields.Many2one("account.tax", "Tax")

    code = fields.Char(string='Code')
    section_code = fields.Char(string='Section Code')

    @api.model
    def create(self, vals):
        if not "company_id" in vals:
            company_id = self.env['res.company'].browse(self.env['res.company'])._company_default_get("pakistan_wht.tax_rate")
            vals["company_id"] = company_id.id

        return super().create(vals)


class ResPartnerIndustry(models.Model):
    _name = "pakistan_wht.tax_category"
    _description = "Pakistan withholding taxes categories"

    name = fields.Char()
    company_id = fields.Many2one("res.company", default=lambda self: self.env['res.company']._company_default_get('pakistan_wht.tax_category'), required=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    tax_rate_ids = fields.One2many('pakistan_wht.tax_rate', 'tax_category_id', string='Tax Rates', ondelete="cascade")


class ResPartner(models.Model):
    _inherit = "res.partner"

    status_wht_id = fields.Selection(wht_dict, string='Withholding Status')
    tax_category_id = fields.Many2one("pakistan_wht.tax_category", string="Tax category")
    tax_category_tax_rate_ids = fields.One2many(related="tax_category_id.tax_rate_ids")

    yearly_wht_forecast_amount = fields.Monetary()
