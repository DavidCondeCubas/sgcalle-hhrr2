# -*- coding: utf-8 -*-

from odoo import models, fields, api

EMPLOYEE_JOB_STATUS = [
    ("trainee", "Trainee"),
    ("probationary", "Probationary"),
    ("confirmed", "Confirmed"),
]

EMPLOYEE_ACTIVE_STATUS = [
    ('regular', 'Regular'),
    ('resigned', 'Resigned'),
    ('terminated', 'Terminated'),
]

class EmployeeExtended(models.Model):
    _inherit = "hr.employee"

    date_of_joining = fields.Date("Date of joining")
    date_of_leaving = fields.Date("Date of leaving")

    health_card_number = fields.Char("Health card number")

    # HCR: Health card number

    hcr_date_of_issue = fields.Date("Health card date of issue")
    hcr_date_of_expiration = fields.Date("Health card date of expiration")

    employee_job_status = fields.Selection(EMPLOYEE_JOB_STATUS, string="Employee job status")
    employee_active_status = fields.Selection(EMPLOYEE_ACTIVE_STATUS, string="Employee active status")

    employee_type_ids = fields.Many2many("hr_extends.employee.type", string="Employee Type")

    hcr_passport_date_of_issue = fields.Date("Passport date of issue")
    hcr_passport_date_of_expiration = fields.Date("Passport date of expiration")

class EmployeeTypes(models.Model):
    _name = "hr_extends.employee.type"
    _description = "Employee type"

    name = fields.Char("Type", translate=True)    
