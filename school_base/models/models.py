# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SchoolCode(models.Model):
    _name = "school_base.school_code"
    _order = "sequence"
    _description = "School code"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    district_code_id = fields.Many2one("school_base.district_code", "District Code")


class SchoolYear(models.Model):
    _name = "school_base.school_year"
    _order = "sequence"
    _description = "School year"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
    district_code_id = fields.Many2one("school_base.district_code", string="District code")

    @api.onchange('school_code_id')
    def _get_school_code_id_domain(self):
        self.ensure_one()
        school_code_ids = self.district_code_id.school_code_ids.ids
        return  {'domain':{'school_code_id':[('id', 'in', school_code_ids)]}}


class GradeLevel(models.Model):
    _name = "school_base.grade_level"
    _order = "sequence"
    _description = "The grade level"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
    district_code_id = fields.Many2one("school_base.district_code", string="District code")

    @api.onchange('school_code_id')
    def _get_school_code_id_domain(self):
        self.ensure_one()
        school_code_ids = self.district_code_id.school_code_ids.ids
        return  {'domain':{'school_code_id':[('id', 'in', school_code_ids)]}}


class DistrictCode(models.Model):
    _name = "school_base.district_code"
    _description = "District code"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_ids = fields.One2many("school_base.school_code", "district_code_id", string="District code")

