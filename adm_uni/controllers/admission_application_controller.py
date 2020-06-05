# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    def get_partner(self):
        return http.request.env["res.users"].browse([http.request.session.uid]).partner_id
    
    @http.route("/admission-university/application", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        contact_id = self.get_partner()
        application_status_ids = http.request.env["adm_uni.application.status"].browse(http.request.env["adm_uni.application.status"].search([])).ids
        contact_time_ids = http.request.env["adm_uni.contact_time"].browse(http.request.env["adm_uni.contact_time"].search([])).ids
        degree_program_ids = http.request.env["adm_uni.degree_program"].browse(http.request.env["adm_uni.degree_program"].search([])).ids
        
        language_ids = http.request.env['adm_uni.languages'].browse(http.request.env['adm_uni.languages'].search([]))
        language_level_ids = http.request.env['adm_uni.languages.level'].browse(http.request.env['adm_uni.languages.level'].search([]))
        
        response = http.request.render('adm_uni.template_admission_application', {
            'contact_id': contact_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'contact_time_ids': contact_time_ids,
            'degree_program_ids': degree_program_ids,
        })
        return response
    
    @http.route("/admission-university/message", auth="public", methods=["POST"], website=True, csrf=False)
    def send_message(self, **params):
        
        print("Params: {}".format(params))
        contact_id = self.get_partner()
        
        upload_file = params["file_upload"]
        message_body = params["message_body"]
        
        message_body=message_body.replace("\n","<br />\n")
        
        MessageEnv = http.request.env["mail.message"]
        message_id = MessageEnv.create({
            'date': datetime.today(),
            'email_from': '"{}" <{}>'.format(contact_id.name, contact_id.email),
            'author_id': contact_id.id,
            'record_name': "",
            "model": "adm_uni.application",
            "res_id": contact_id.uni_application_id.id,
            "message_type": "comment",
            "subtype_id": 1,
            "body": "<p>{}</p>".format(message_body),
        })
        
        AttachmentEnv = http.request.env["ir.attachment"]
        
        if upload_file:
            file_id = AttachmentEnv.sudo().create({
                'name': upload_file.filename,
                'datas_fname': upload_file.filename,
                'res_name': upload_file.filename,
                'type': 'binary',   
                'res_model': 'adm_uni.application',
                'res_id': contact_id.uni_application_id,
                'datas': base64.b64encode(upload_file.read()),
            })
        
        return http.request.redirect('/admission-university/application')
        
        #===============================================================================================================
        # return "Ok"
        #===============================================================================================================

    @http.route("/admission-university/application", auth="public", methods=["POST"], website=True, csrf=False)
    def add_admission(self, **params):
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""
            
        # Personal Info
        gender = params["selGender"]
        father_name = params["txtFatherName"]
        mother_name = params["txtMotherName"]
        
        # School information
        previous_school = params["txtPreviousSchool"]
        gpa = params["txtGPA"]
        cumulative_grades = params["txtCumulativeGrade"]
        regional_exam_grade = params["txtRegionalExam"]
        bac_grade = params["txtBACGrade"]
        
        # Documentation 
        letter_of_motivation_file = params["fileLetterOfMotivation"]
        cv_file = params["fileCV"]
        grade_transcript_file = params["fileGradeTranscript"]

        letters_of_recommendation_file = params["fileLettersOfRecommendation"]
        
        contact_time_id = params["selPreferredContactTime"]
        preferred_degree_program = params["selPreferredDegreeProgram"]
        
        new_application_dict = {
            'gender': gender,
            'father_name': father_name,
            'mother_name': mother_name,
            
            'previous_school': previous_school,
            'gpa': gpa,
            'cumulative_grades': cumulative_grades,
            'regional_exam_grade': regional_exam_grade,
            'bac_grade': bac_grade,
            
            'contact_time_id': contact_time_id,
            'preferred_degree_program': preferred_degree_program,
        }
        
        contact_id = self.get_partner()
        application_id = contact_id.uni_application_id
        application_id.write(new_application_dict)

        AttachmentEnv = http.request.env["ir.attachment"]
        motivation_id = AttachmentEnv.sudo().create({
            'name': letter_of_motivation_file.filename,
            'datas_fname': letter_of_motivation_file.filename,
            'res_name': letter_of_motivation_file.filename,
            'type': 'binary',   
            'res_model': 'adm_uni.application',
            'res_id': application_id.id,
            'datas': base64.b64encode(letter_of_motivation_file.read()),
        })
        cv_id = AttachmentEnv.sudo().create({
            'name': cv_file.filename,
            'datas_fname': cv_file.filename,
            'res_name': cv_file.filename,
            'type': 'binary',   
            'res_model': 'adm_uni.application',
            'res_id': application_id.id,
            'datas': base64.b64encode(cv_file.read()),
        })
        grade_transcript_id = AttachmentEnv.sudo().create({
            'name': grade_transcript_file.filename,
            'datas_fname': grade_transcript_file.filename,
            'res_name': grade_transcript_file.filename,
            'type': 'binary',   
            'res_model': 'adm_uni.application',
            'res_id': application_id.id,
            'datas': base64.b64encode(grade_transcript_file.read()),
        })
        letters_of_recommendation_id = AttachmentEnv.sudo().create({
            'name': letters_of_recommendation_file.filename,
            'datas_fname': letters_of_recommendation_file.filename,
            'res_name': letters_of_recommendation_file.filename,
            'type': 'binary',   
            'res_model': 'adm_uni.application',
            'res_id': application_id.id,
            'datas': base64.b64encode(letters_of_recommendation_file.read()),
        })
        
        contact_names = post_parameters().getlist("txtContactName")
        contact_ids    = post_parameters().getlist("txtContactId")
        
        languages = post_parameters().getlist("selLanguage")
        language_levels = post_parameters().getlist("selLanguageLevel")
        
        # Adding Languages
        LanguageEnv = http.request.env["adm_uni.application.languages"]
        for i, language in enumerate(languages):
            if language != "-1" and language_levels[i] != "-1":
                LanguageEnv.create({
                    "language_id": language,
                    "language_level_id": language_levels[i],
                    "application_id":   application_id.id,
                })
        
        # Adding contact
        OtherContactsEnv = http.request.env["adm_uni.application.other_contacts"]
        for i, contact_name in enumerate(contact_names):
            if (len(contact_name.strip()) > 0 and
                len(contact_ids[i].strip()) > 0):
                
                OtherContactsEnv.create({
                    "contact_name": contact_name,
                    "contact_identification": contact_ids[i],
                    "application_id":   application_id.id,
                })
            
        application_id.letter_of_motivation_id = motivation_id
        application_id.cv_id = cv_id
        application_id.grade_transcript_id = grade_transcript_id
        application_id.letters_of_recommendation_id = letters_of_recommendation_id
        
#         PartnerEnv = http.request.env["res.partner"]
        
        contact_id.sudo().write({"is_in_application": True})
        
        return "Exito, se ha enviado el estudiante: '{}'".format(application_id.name)
