'''
Created on Feb 1, 2020

@author: LuisMora
'''
from odoo import models, fields

class ResPartnerExtended(models.Model):
    _inherit = ["res.partner"]
    
    uni_application_id = fields.Many2one("adm_uni.application", string="Application")
    uni_inquiry_id = fields.Many2one("adm_uni.inquiry", string="Inquiry")
    is_in_application = fields.Boolean("Is in Application?")
