# -*- coding: utf-8 -*-

from odoo import models, fields


class AdmissionLanguages(models.Model):
    _name = "adm_uni.languages"
    
    name = fields.Char("Name", required=True)
    
class AdmissionLanguageLevels(models.Model):
    _name = "adm_uni.languages.level"
    
    name = fields.Char("Name", required=True)
    