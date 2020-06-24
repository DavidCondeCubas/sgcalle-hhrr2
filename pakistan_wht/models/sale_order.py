# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError, Warning
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class SaleOrderForStudents(models.Model):
    _inherit = "sale.order"

    accumulated_amount = fields.Monetary(string='accumulated amount', readonly=True, compute="_compute_accumulated_amount")
    partner_yearly_wht_forecast_amount = fields.Monetary(related="partner_id.yearly_wht_forecast_amount")
    exempt_upto = fields.Monetary(string='Exempt upto', readonly=True, compute="_compute_exempt_upto")
    exempt_upto_tax_percent = fields.Float(string='Exempt upto', readonly=True, compute="_compute_exempt_upto_tax_percent")

    def _compute_exempt_upto_tax_percent(self):
        for sale in self:
            tax_rate_ids = sale.partner_id.tax_category_id.tax_rate_ids.filtered(
                lambda self: sale.partner_id.status_wht_id == self.status).sorted("exempt_upto", True)

            tax_id = False
            amount_to_compare = sale.accumulated_amount
            yearly_wht_forecast_amount = sale.partner_id.yearly_wht_forecast_amount
            if yearly_wht_forecast_amount > 0:
                amount_to_compare = yearly_wht_forecast_amount

            if tax_rate_ids:
                for tax_aux_id in tax_rate_ids:
                    if amount_to_compare < tax_aux_id.exempt_upto:
                        continue
                    else:
                        tax_id = tax_aux_id
             
            if tax_id:
                sale.exempt_upto_tax_percent = tax_id.tax_id.amount
            else:
                sale.exempt_upto_tax_percent = 0.0
            

    def _compute_exempt_upto(self):
        for sale in self:
            tax_rate_ids = sale.partner_id.tax_category_id.tax_rate_ids.filtered(
                lambda self: sale.partner_id.status_wht_id == self.status).sorted("exempt_upto", True)

            tax_id = False
            amount_to_compare = sale.accumulated_amount
            yearly_wht_forecast_amount = sale.partner_id.yearly_wht_forecast_amount
            if yearly_wht_forecast_amount > 0:
                amount_to_compare = yearly_wht_forecast_amount

            if tax_rate_ids:
                for tax_aux_id in tax_rate_ids:
                    if amount_to_compare < tax_aux_id.exempt_upto:
                        continue
                    else:
                        tax_id = tax_aux_id
             
            if tax_id:
                sale.exempt_upto = tax_id.exempt_upto
            else:
                sale.exempt_upto = 0.0

    def _compute_accumulated_amount(self):
        for sale in self:

            company_id = self.env["res.company"].browse(self._context.get("allowed_company_ids"))
            fiscal_year_range = company_id.compute_fiscalyear_dates( datetime.now())

            all_partner_sale = self.env["sale.order"].search([("partner_id", "=", sale.partner_id.id), ("company_id", "=", company_id.id)]).filtered(
                lambda self: fiscal_year_range["date_from"] < self.date_order < fiscal_year_range["date_to"])
            amount_sales_sum = sum([record.amount_total for record in all_partner_sale])
            sale.accumulated_amount = amount_sales_sum

    @api.model
    def create(self, vals):
        sale_ids = super().create(vals)

        for sale in sale_ids:
            # We get the taxes from the contact
            amount_sales_sum = sale.accumulated_amount

            tax_rate_ids = sale.partner_id.tax_category_id.tax_rate_ids.filtered(
                lambda self: sale.partner_id.status_wht_id == self.status).sorted("exempt_upto", True)

            amount_to_compare = amount_sales_sum
            yearly_wht_forecast_amount = sale.partner_id.yearly_wht_forecast_amount
            if yearly_wht_forecast_amount > 0:
                amount_to_compare = yearly_wht_forecast_amount

            if tax_rate_ids:
                tax_id = False
                for tax_aux_id in tax_rate_ids:
                    if amount_to_compare < tax_aux_id.exempt_upto:
                        continue
                    else:
                        tax_id = tax_aux_id

                if tax_id:
                    if yearly_wht_forecast_amount > 0:
                        sale.order_line.write(
                            {"taxes_id": [(4, tax_id.tax_id.id, 0)]})

        return sale_ids

    def write(self, vals):
        sale_ids = super().write(vals)

        for sale in self:
            # We get the taxes from the contact
            amount_sales_sum = sale.accumulated_amount

            tax_rate_ids = sale.partner_id.tax_category_id.tax_rate_ids.filtered(
                lambda self: sale.partner_id.status_wht_id == self.status).sorted("exempt_upto", True)

            amount_to_compare = amount_sales_sum
            yearly_wht_forecast_amount = sale.partner_id.yearly_wht_forecast_amount
            if yearly_wht_forecast_amount > 0:
                amount_to_compare = yearly_wht_forecast_amount

            if tax_rate_ids:
                tax_id = False
                for tax_aux_id in tax_rate_ids:
                    if amount_to_compare < tax_aux_id.exempt_upto:
                        continue
                    else:
                        tax_id = tax_aux_id

                if tax_id:
                    if yearly_wht_forecast_amount > 0:
                        sale.order_line.write(
                            {"tax_id": [(4, tax_id.tax_id.id, 0)]})
#                        raise Warning("Message")
                        # mess = {
                        #     'title': _('Not enough inventory!'),
                        #     'message': _("Wtf?")
                        # }
                        # return {'warning': mess}

        return sale_ids
