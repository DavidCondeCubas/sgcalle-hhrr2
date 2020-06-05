'''
Created on Feb 14, 2020

@author: LuisMora
'''

from odoo import fields, models

class PreviousSchoolDescription(models.Model):
    _name = "adm.previous_school_description"
    
    application_id = fields.Many2one("adm.application")
    
    name = fields.Char("School Name")
    street = fields.Char("School Name")
    city = fields.Char("School Name")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char("School Name")
    phone = fields.Char("School Name")
    from_date = fields.Date("School Name")
    to_date = fields.Date("School Name")
    grade_completed = fields.Char("School Name")
    