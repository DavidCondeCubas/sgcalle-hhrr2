# -*- coding: utf-8 -*-

from odoo import models, fields


class AdmissionLanguages(models.Model):
    _name = "adm.language"
    
    name = fields.Char("Name", required=True)
    
class AdmissionLanguageLevels(models.Model):
    _name = "adm.language.level"
    
    name = fields.Char("Name", required=True)
    
class LanguageTypeOfSkill(models.Model):
    _name = "adm.language.skill.type"
    
    name = fields.Char("Type")