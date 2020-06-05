# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class AccountAnalyticGroup(models.Model):

    _inherit = "account.analytic.group"

    analytic_code = fields.Char("Analytic Group")
    
