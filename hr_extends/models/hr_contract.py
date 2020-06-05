# -*- coding: utf-8 -*-

from odoo import models, fields, api

EMPLOYEE_STATUS = [
    ("full_time", "Full time"),
    ("part_time", "Part time"),
]

class Contract(models.Model):
    _inherit = "hr.contract"


    employee_status = fields.Selection(EMPLOYEE_STATUS, string="Employee Status")
    test = fields.Char("Cosas")

    last_review_date = fields.Date("Last review date")
    next_review_date = fields.Date("Next review date")
