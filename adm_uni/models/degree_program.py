# -*- coding: utf-8 -*-
from odoo import models, fields

class AdmissionDegreeProgram(models.Model):
    _name = "adm_uni.degree_program"
    
    name = fields.Char("Name")
    