# -*- coding: utf-8 -*-

import base64
import os
import logging

from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = "res.company"
    
    # def _get_logo(self):
    #     return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'), 'rb') .read())

    vertical_logo = fields.Binary(string="Company Logo", readonly=False)
    hr_officer = fields.Many2one("hr.employee", string="HR/Procurement Officer")
    director_of_hr = fields.Many2one("hr.employee", string="Director of human resources")

