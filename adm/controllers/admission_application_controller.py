# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import base64
import itertools


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    def get_partner(self):
        return http.request.env["res.users"].browse([http.request.session.uid]).partner_id
    
    @http.route("/admission/applications", auth="public", methods=["GET"], website=True)
    def admission_list_web(self, **params):
        user_contact = self.get_partner()
        ApplicationEnv = http.request.env["adm.application"]
        
        application_ids = ApplicationEnv.search([("family_id", "=", user_contact.parent_id.id)])
        
        response = http.request.render('adm.template_admission_application_list', {
            "application_ids": application_ids,
        })
        return response
    
    @http.route("/admission/applications/<int:application_id>", auth="public", methods=["GET"], website=True)
    def admission_web(self, application_id):
        contact_id = self.get_partner()
        ApplicationEnv = http.request.env["adm.application"]
        
        contact_time_ids = http.request.env["adm.contact_time"].browse(http.request.env["adm.contact_time"].search([])).ids
        degree_program_ids = http.request.env["adm.degree_program"].browse(http.request.env["adm.degree_program"].search([])).ids
        
        application_status_ids = http.request.env["adm.application.status"].browse(http.request.env["adm.application.status"].search([])).ids
        
        student_application = ApplicationEnv.browse([application_id])
        language_ids = http.request.env['adm.language'].browse(http.request.env['adm.language'].search([]))
        language_level_ids = http.request.env['adm.language.level'].browse(http.request.env['adm.language.level'].search([]))
        
        response = http.request.render('adm.template_application_menu_progress', {
            'contact_id': contact_id,
            'application_id': application_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'student_application': student_application,
            'contact_time_ids': contact_time_ids,
            'degree_program_ids': degree_program_ids,
            'current_url': http.request.httprequest.full_path,
        })
        return response
    
    @http.route("/admission/applications/message/<int:application_id>", auth="public", methods=["POST"], website=True, csrf=False)
    def send_message(self, **params):
        
        print("Params: {}".format(params))
        contact_id = self.get_partner()
        application_id = params["application_id"]
        upload_file = params["file_upload"]
        message_body = params["message_body"]
        
        message_body = message_body.replace("\n", "<br />\n")
        
        MessageEnv = http.request.env["mail.message"]
        message_id = MessageEnv.sudo().create({
            'date': datetime.today(),
            'email_from': '"{}" <{}>'.format(contact_id.name, contact_id.email),
            'author_id': contact_id.id,
            'record_name': "",
            "model": "adm.application",
            "res_id": application_id,
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
                'res_model': 'adm.application',
                'res_id': application_id,
                'datas': base64.b64encode(upload_file.read()),
            })
        
        url_redirect = '/admission/applications/{}/document-upload'.format(application_id)
        return http.request.redirect(url_redirect)
    
        # return http.request.redirect('/admission/applications')
        
        #===============================================================================================================
        # return "Ok"
        #===============================================================================================================

    @http.route("/admission/applications/<int:application_id>", auth="public", methods=["POST"], website=True, csrf=False)
    def add_admission(self, **params):
        
        application_id = params["application_id"]
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""

        full_name = "{}, {}{}".format(params["txtLastName"], "" if not params["txtMiddleName"] else params["txtMiddleName"] + " ",
                                      params["txtFirstName"])

        new_parent_dict = {'name': full_name,
                           'first_name': params["txtFirstName"],
                           'middle_name': params["txtMiddleName"],
                           'last_name': params["txtLastName"],
                           'salutation': params["txtSalutation"],
                           'email': params["txtEmail"],
                           'mobile': params["txtCellPhone"],
                           'phone': params["txtHomePhone"],
                           'street': params["txtStreetAddress"],
                           # 'country': params["selCountry"],
                           'zip': params["txtZip"]}

        if params["selState"] != "-1":
            new_parent_dict["state"] = params["selState"]

        partners = http.request.env['res.partner']
        id_parent = partners.create(new_parent_dict)

        # Create a lead
        print("application_id: {}".format(application_id))

        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        grade_level_list = post_parameters().getlist("selStudentGradeLevel")
        school_year_list = post_parameters().getlist("selStudentSchoolYear")
        current_school_list = post_parameters().getlist("txtStudentCurrentSchool")
        gender_list = post_parameters().getlist("selStudentGender")
        InquiryEnv = http.request.env["adm.inquiry"]

        for index_student in range(students_total):
            # print("{} -> {}".format(first_name_list, index_student))
            first_name = first_name_list[index_student]
            middle_name = middle_name_list[index_student]
            last_name = last_name_list[index_student]
            birthday = birthday_list[index_student]
            grade_level = grade_level_list[index_student]
            school_year = school_year_list[index_student]
            current_school = current_school_list[index_student]
            gender = gender_list[index_student]
            
            full_name_student = "{}, {}{}".format(last_name, "" if not middle_name else middle_name + " ", first_name)

            id_student = InquiryEnv.create({
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'gender':  self.env.ref('adm.gender_male').id,
                'birthday': birthday,
                'email': params["txtEmail"],
                'school_year': school_year,
                'grade_level': grade_level,
                'current_school': current_school,
                'responsible_id': id_parent.id
            })
            id_students.append(id_student)
        
        return http.request.redirect('/admission/applications')

    # adm.previous_school_description
    def set_house_address(self, application_id, params):
        if "has_house_address" in params:
            
            post_params = post_parameters()
            house_address_ids = post_params.getlist("house_address_id")
            
            house_address_ids = list(map(int, house_address_ids))
            
            house_address_name = post_params.getlist("house_address_name")
            house_address_country_id = post_params.getlist("house_address_country_id")
            house_address_state_id = post_params.getlist("house_address_state_id")
            house_address_city = post_params.getlist("house_address_city")
            house_address_zip = post_params.getlist("house_address_zip")
            house_address_street = post_params.getlist("house_address_street")
            house_address_phone = post_params.getlist("house_address_phone")
            
            application = http.request.env["adm.application"].browse([application_id])
            
            HouseAddressEnv = http.request.env["adm.house_address"]
            
            # First, delete all that are not in the form, that's why the user clicked remove button.
            all_ids = set(application.sudo().partner_id.parent_id.house_address_ids.ids)
            form_ids = {id for id in house_address_ids if id != -1}
             
            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [ (2, id, 0) for id in ids_to_delete ]
             
            if unlink_commands:
                application.sudo().partner_id.parent_id.write({"house_address_ids": unlink_commands})
             
            # PartnerEnv = http.request.env["res.partner"]
            
            for id, name, country_id, state_id, city, zip, street, phone \
            in itertools.zip_longest(house_address_ids, house_address_name, house_address_country_id,
                   house_address_state_id, house_address_city, house_address_zip, house_address_street,
                   house_address_phone, fillvalue=False):
                if id != -1:
                    partner = HouseAddressEnv.browse([id])
                    partner.sudo().write({
                        "name": name,
                        "country_id": country_id,
                        "state_id": state_id,
                        "city": city,
                        "zip": zip,
                        "street": street,
                        "phone": phone,
                    })
                else:
                    partner = HouseAddressEnv.sudo().create({
                        "name": name,
                        "country_id": country_id,
                        "state_id": state_id,
                        "city": city,
                        "zip": zip,
                        "street": street,
                        "phone": phone,
                        "family_id": application.partner_id.parent_id.id
                    })
                    # application.sudo().write({"house_address_ids": [(4, partner.sudo().id, 0)]})
            
    def set_medical_info(self, application_id, params):
        if "has_medical_info" in params:
            
            post_params = post_parameters()
            
            
            application = http.request.env["adm.application"].browse([application_id])
            
            # -- Conditions -- #
            medical_conditions_ids = post_params.getlist("medical_condition_id")
            medical_allergies_ids = post_params.getlist("medical_allergy_id")
            medical_medications_ids = post_params.getlist("medical_medication_id")
            
            medical_conditions_ids = list(map(int, medical_conditions_ids))
            medical_allergies_ids = list(map(int, medical_allergies_ids))
            medical_medications_ids = list(map(int, medical_medications_ids))
            
            medical_condition_name = post_params.getlist("medical_condition_name")
            medical_condition_comment = post_params.getlist("medical_condition_comment")

            medical_allergy_name = post_params.getlist("medical_allergy_name")
            medical_allergy_comment = post_params.getlist("medical_allergy_comment")

            medical_medication_name = post_params.getlist("medical_medication_name")
            medical_medication_comment = post_params.getlist("medical_medication_comment")
            
            
            # First, delete all that are not in the form, that's why the user clicked remove button.
            
            # -- Conditions --#
            all_ids = set(application.sudo().medical_conditions_ids.ids)
            form_ids = {id for id in medical_conditions_ids if id != -1}
             
            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [ (2, id, False) for id in ids_to_delete ]
             
            if unlink_commands:
                application.sudo().write({"medical_conditions_ids": unlink_commands})
            #-------------------

            # -- Allergies --#
            all_ids = set(application.sudo().medical_allergies_ids.ids)
            form_ids = {id for id in medical_allergies_ids if id != -1}
             
            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [ (2, id, False) for id in ids_to_delete ]
             
            if unlink_commands:
                application.sudo().write({"medical_allergies_ids": unlink_commands})
            #-------------------

            # -- Medications --#
            all_ids = set(application.sudo().medical_medications_ids.ids)
            form_ids = {id for id in medical_medications_ids if id != -1}
             
            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [ (2, id, False) for id in ids_to_delete ]
             
            if unlink_commands:
                application.sudo().write({"medical_medications_ids": unlink_commands})
            #-------------------
            
            # -- Conditions -- #
            conditions_create_commands = list()
            conditions_write_comands = list()

            for id, name, comment \
            in itertools.zip_longest(medical_conditions_ids, medical_condition_name, medical_condition_comment,
                                     fillvalue=False):
                if id != -1:
                    conditions_write_comands.append( (1, id, {"name": name, "comment": comment}) )
                else:
                    conditions_create_commands.append( (0, False, {"name": name, "comment": comment}) )

            conditions_commands = conditions_create_commands + conditions_write_comands
            #-------------------
            
            # -- Allergies -- #
            allergies_create_commands = list()
            allergies_write_comands = list()

            for id, name, comment \
            in itertools.zip_longest(medical_allergies_ids, medical_allergy_name, medical_allergy_comment,
                                     fillvalue=False):
                if id != -1:
                    allergies_create_commands.append( (1, id, {"name": name, "comment": comment}) )
                else:
                    allergies_write_comands.append( (0, False, {"name": name, "comment": comment}) )

            allergies_commands = allergies_write_comands + allergies_create_commands
            #-------------------
            
            # -- Medications -- #
            medications_create_commands = list()
            medications_write_comands = list()

            for id, name, comment \
            in itertools.zip_longest(medical_medications_ids, medical_medication_name, medical_medication_name,
                                     fillvalue=False):
                if id != -1:
                    conditions_write_comands.append( (1, id, {"name": name, "comment": comment}) )
                else:
                    medications_write_comands.append( (0, False, {"name": name, "comment": comment}) )

            medications_commands = medications_create_commands + medications_write_comands
            #-------------------

            application.sudo().write({
                "medical_conditions_ids": conditions_commands,
                "medical_allergies_ids": allergies_commands,
                "medical_medications_ids": medications_commands,
            })

    def set_additional_student(self, application_id, params):
        if "is_additional_student_info" in params:
            
            # post_params = post_parameters()
            
            #===========================================================================================================
            # first_language_skills = post_params.getlist("first_language_skills")
            # first_language_skills = list(map(int, first_language_skills))
            # 
            # second_language_skills = post_params.getlist("second_language_skills")
            # second_language_skills = list(map(int, second_language_skills))
            # 
            # third_language_skills = post_params.getlist("third_language_skills")
            # third_language_skills = list(map(int, third_language_skills))
            # 
            #===========================================================================================================
            application = http.request.env["adm.application"].browse([application_id])

            application.sudo().write({
                "first_language_skill_write": False,
                "first_language_skill_read": False,
                "first_language_skill_speak": False,
                "first_language_skill_listen": False,
                
                "second_language_skill_write": False,
                "second_language_skill_read": False,
                "second_language_skill_speak": False,
                "second_language_skill_listen": False,
                
                "third_language_skill_write": False,
                "third_language_skill_read": False,
                "third_language_skill_speak": False,
                "third_language_skill_listen": False,
            })
    
    def set_previous_school(self, application_id, params):
        if "has_previous_schools" in params:
             
            post_params = post_parameters()
            previous_school_ids = post_params.getlist("previous_school_id")
            previous_school_ids = list(map(int, previous_school_ids))
            
            previous_school_names = post_params.getlist("previous_school_name")
            previous_school_street = post_params.getlist("previous_school_street")
            previous_school_city = post_params.getlist("previous_school_city")
            previous_school_country = post_params.getlist("previous_school_country")
            previous_school_state = post_params.getlist("previous_school_state")
            previous_school_zip = post_params.getlist("previous_school_zip")
            previous_school_phone = post_params.getlist("previous_school_phone")
            previous_school_fromdate = post_params.getlist("previous_school_fromdate")
            previous_school_todate = post_params.getlist("previous_school_todate")
            previous_school_gradecompleted = post_params.getlist("previous_school_gradecompleted")
             
            PreviousSchoolDescriptionEnv = http.request.env["adm.previous_school_description"]
            application = http.request.env["adm.application"].browse([application_id])
             
            # First, delete all that are not in the form, that's why the user clicked remove button.
            all_ids = set(application.previous_school_ids.ids)
            form_ids = {id for id in previous_school_ids if id != -1}
            
            ids_to_delete = all_ids ^ form_ids
            PreviousSchoolDescriptionEnv.browse(ids_to_delete).unlink()
             
            for id, name, street, city, state, country, zip, phone, from_date, to_date, grade_completed \
            in itertools.zip_longest(previous_school_ids, previous_school_names, previous_school_street,
                                     previous_school_city, previous_school_state, previous_school_country,
                                     previous_school_zip, previous_school_phone, previous_school_fromdate,
                                     previous_school_todate, previous_school_gradecompleted,
                                     fillvalue=False):
                if id != -1:
                    PreviousSchoolDescriptionEnv.browse([id]).write({
                        "name": name,
                        "city": city,
                        "country_id": country,
                        "state_id": state,
                        "zip": zip,
                        "street": street,
                        "phone": phone,
                        "from_date": from_date,
                        "to_date": to_date,
                        "grade_completed": grade_completed,
                    })
                    pass
                else:
                    PreviousSchoolDescriptionEnv.create({
                        "application_id": application_id,
                        "name": name,
                        "city": city,
                        "state_id": state,
                        "zip": zip,
                        "street": street,
                        "phone": phone,
                        "from_date": from_date,
                        "to_date": to_date,
                        "grade_completed": grade_completed,
                    })
        pass
    
    def set_contact(self, application_id, params):
        if "has_contact" in params:
             
            post_params = post_parameters()
            contact_ids = post_params.getlist("contact_id")
            contact_ids = list(map(int, contact_ids))
            
            contact_existing_id = post_params.getlist("contact_existing_id")
            contact_existing_id = list(map(int, contact_existing_id))
            
            new_contact_id = post_params.getlist("new_contact_id")
            new_contact_id = list(map(int, new_contact_id))
            
            relationship_type = post_params.getlist("relationship_type")
            relation_partner_mobile = post_params.getlist("relation_partner_mobile")
            relation_partner_phone = post_params.getlist("relation_partner_phone")
            relation_partner_email = post_params.getlist("relation_partner_email")
            relationship_house = post_params.getlist("relationship_house")
            relationship_is_emergency_contact = post_params.getlist("relationship_is_emergency_contact")
            
            # From new contacts
            new_partner_name = post_params.getlist("new_partner_name")
            new_partner_mobile = post_params.getlist("new_partner_mobile")
            new_partner_phone = post_params.getlist("new_partner_phone")
            new_partner_email = post_params.getlist("new_partner_email")
            new_relationship_type = post_params.getlist("new_relationship_type")
            new_relationship_house = post_params.getlist("new_relationship_house")
            new_relationship_is_emergency_contact = post_params.getlist("new_relationship_is_emergency_contact")
            
            PartnerEnv = http.request.env["res.partner"]
            RelationshipEnv = http.request.env["adm.relationship"]
            application = http.request.env["adm.application"].browse([application_id])
            
            # First, delete all that are not in the form, that's why the user clicked remove button.
            ids_to_delete = {relation.id for relation in application.relationship_ids if not relation.partner_2.id in contact_ids}
            unlink_commands = [ (2, id, 0) for id in ids_to_delete ]

            application.sudo().write({
                "relationship_ids": unlink_commands,
            })
            
            # Link all existing ids.
            application.sudo().write({
                "relationship_ids": [(0, 0, {"partner_1": application.partner_id.id,
                                             "partner_2": id,
                 }) for id in contact_existing_id],
            })

            for id, type, mobile, phone, email, house_address_id, is_emergency_contact \
            in  itertools.zip_longest(contact_ids, relationship_type, relation_partner_mobile,
                                      relation_partner_phone, relation_partner_email, relationship_house,
                                      relationship_is_emergency_contact,
                                      fillvalue=False):
                if id != -1:
                    relationship = application.relationship_ids.filtered(lambda relation : relation.partner_2.id == id)
                    relationship.sudo().write({
                        "relationship_type": type,
                        "is_emergency_contact": is_emergency_contact,
                    })
                    PartnerEnv.sudo().browse([id]).write({
                        "phone": phone,
                        "mobile": mobile,
                        "email": email,
                        "email": email,
                        "house_address_id": house_address_id,
                    })
                    
            for name, mobile, phone, email, type, house_address_id, is_emergency_contact \
            in  itertools.zip_longest(new_partner_name, new_partner_mobile, new_partner_phone, 
                                      new_partner_email, new_relationship_type, new_relationship_house,
                                      new_relationship_is_emergency_contact,
                                      fillvalue=False):
                new_partner = PartnerEnv.sudo().create({
                    "name": name,
                    "parent_id": application.partner_id.parent_id.id,
                    "phone": phone,
                    "mobile": mobile,
                    "email": email,
                    "house_address_id": house_address_id,
                })
                
                application.sudo().write({
                    "relationship_ids": [(0, 0, {"partner_2": new_partner.id,
                                                 "relationship_type": type,
                                                 "is_emergency_contact": is_emergency_contact,
                    })]
                })
        pass
            
    @http.route("/admission/applications/<int:application_id>/write", auth="public", methods=["POST"], website=True, csrf=False)
    def write_application(self, application_id, **params):
        field_ids = http.request.env.ref("adm.model_adm_application").sudo().field_id
        fields = [field_id.name for field_id in field_ids]
        keys = params.keys() & fields
        result = {k:params[k] for k in keys}
        field_types = {field_id.name:field_id.ttype for field_id in field_ids}
        
        # if field_id.ttype != 'one2many' and field_id.ttype != 'many2many'
        
        self.set_house_address(application_id, params)
        self.set_previous_school(application_id, params)
        self.set_additional_student(application_id, params)
        self.set_contact(application_id, params)
        self.set_medical_info(application_id, params)
            
        many2one_fields = [name for name, value in field_types.items() if value == "many2one"]
        for key in result.keys():
            if key in many2one_fields:
                result[key] = int(result[key])
                if result[key] == -1:
                    result[key] = False
                    pass    
        
        #===============================================================================================================
        # one2many_fields = [name for name, value in field_types.items() if value == "one2many"]
        # many2many_fields = [name for name, value in field_types.items() if value == "many2many"]
        #  
        # for key in post_params.keys():
        #     if key in many2many_fields:
        #         pass
        #===============================================================================================================
        
        if result:
            http.request.env["adm.application"].browse([application_id]).sudo().write(result)
            
        return http.request.redirect(http.request.httprequest.referrer)
    
    @http.route("/admission/applications/<int:application_id>/instructions-resources", auth="public", methods=["GET"], website=True, csrf=False)
    def instructions_resources(self, **params):
        return http.request.render("adm.template_application_menu_instructions", {
            "application_id": params["application_id"]
        })
    
    @http.route("/admission/applications/<int:application_id>/info", auth="public", methods=["GET"], website=True, csrf=False)
    def info(self, **params):
        
        ApplicationEnv = http.request.env["adm.application"]
        CountryEnv = http.request.env['res.country']
        GenderEnv = http.request.env['adm.gender']
        application = ApplicationEnv.browse([params["application_id"]])
        countries = CountryEnv.browse(CountryEnv.search([]))
        genders = GenderEnv.browse(GenderEnv.search([]))
        
        LanguageEnv = http.request.env["adm.language"]
        languages = LanguageEnv.browse(LanguageEnv.search([])).ids
        
        return http.request.render("adm.template_application_menu_info", {
            "application_id": params["application_id"],
            "application": application,
            "countries": countries.ids,
            "student": application.partner_id,
            "languages": languages,
            "genders": genders,
        })
    
    @http.route("/admission/applications/<int:application_id>/previous-school", auth="public", methods=["GET"], website=True, csrf=False)
    def previous_school(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        CountryEnv = http.request.env['res.country']
        StateEnv = http.request.env['res.country.state']
        
        application = ApplicationEnv.browse([params["application_id"]])
        countries = CountryEnv.browse(CountryEnv.search([]))
        states = StateEnv.browse(StateEnv.search([]))
        
        LanguageEnv = http.request.env["adm.language"]
        languages = LanguageEnv.browse(LanguageEnv.search([])).ids
        
        return http.request.render("adm.template_application_menu_previous_school", {
            "application_id": params["application_id"],
            "application": application,
            "countries": countries.ids,
            "states": states.ids,
            "student": application.partner_id,
            "languages": languages,
        })
    
    @http.route("/admission/applications/<int:application_id>/additional-student-info", auth="public", methods=["GET"], website=True, csrf=False)
    def additional_student_info(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        
        LanguageEnv = http.request.env["adm.language"]
        languages = LanguageEnv.browse(LanguageEnv.search([])).ids
        
        return http.request.render("adm.template_application_menu_student_info", {
            "application_id": params["application_id"],
            "application": application,
            "languages": languages,
        })
    
    @http.route("/admission/applications/<int:application_id>/household-1", auth="public", methods=["GET"], website=True, csrf=False)
    def household_1(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        return http.request.render("adm.template_application_menu_household1", {
            "application_id": params["application_id"],
            "application": application,
        })
    
    @http.route("/admission/applications/<int:application_id>/household-2", auth="public", methods=["GET"], website=True, csrf=False)
    def household_2(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        return http.request.render("adm.template_application_menu_household2", {
            "application_id": params["application_id"],
            "application": application,
        })
    
    @http.route("/admission/applications/<int:application_id>/house-address", auth="public", methods=["GET"], website=True, csrf=False)
    def house_address(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        CountryEnv = http.request.env['res.country']
        StateEnv = http.request.env['res.country.state']
        
        application = ApplicationEnv.browse([params["application_id"]])
        countries = CountryEnv.browse(CountryEnv.search([]))
        states = StateEnv.browse(StateEnv.search([]))
        
        return http.request.render("adm.template_application_menu_house_address", {
            "application_id": params["application_id"],
            "application": application,
            "countries": countries.ids,
            "states": states.ids,
        })
    
    @http.route("/admission/applications/<int:application_id>/family-info", auth="public", methods=["GET"], website=True, csrf=False)
    def family_info(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        
        PartnerEnv = http.request.env["res.partner"]
        relation_contact_ids = {relation.partner_2.id for relation in application.relationship_ids}
        pertner_search_ids = PartnerEnv.sudo().search([('is_company', '=', False)]).filtered(lambda x : x.id in application.partner_id.parent_id.child_ids.ids and x.id != application.partner_id.id and not x.id in relation_contact_ids)
        
        partners = PartnerEnv.browse(pertner_search_ids)
        
        return http.request.render("adm.template_application_menu_family_info", {
            "application_id": params["application_id"],
            "application": application,
            "partners": partners.ids,
        })
    
    @http.route("/admission/applications/<int:application_id>/medical-info", auth="public", methods=["GET"], website=True, csrf=False)
    def medical_info(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        return http.request.render("adm.template_application_menu_medical_info", {
            "application_id": params["application_id"],
            "application": application,
        })
    
    @http.route("/admission/applications/<int:application_id>/alumni-currently-enrolled-student", auth="public", methods=["GET"], website=True, csrf=False)
    def alumni_currently_enrolled_student(self, **params):
        return http.request.render("adm.template_application_menu_alumni_currently_enrolled_students", {
            "application_id": params["application_id"]
        })
    
    @http.route("/admission/applications/<int:application_id>/institutional-fee-declaration-form", auth="public", methods=["GET"], website=True, csrf=False)
    def institutional_fee_declaration_form(self, **params):
        return http.request.render("adm.template_application_menu_institutional_fee_declaration", {
            "application_id": params["application_id"]
        })
    
    @http.route("/admission/applications/<int:application_id>/policy-agreement", auth="public", methods=["GET"], website=True, csrf=False)
    def policy_agreement(self, **params):
        return http.request.render("adm.template_application_menu_admissions_policy_agreement", {
            "application_id": params["application_id"]
        })
    
    @http.route("/admission/applications/<int:application_id>/references", auth="public", methods=["GET"], website=True, csrf=False)
    def references(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        
        return http.request.render("adm.template_application_menu_references", {
            "application": application,
            "application_id": params["application_id"],
        })
    
    @http.route("/admission/applications/<int:application_id>/recommendation", auth="public", methods=["GET"], website=True, csrf=False)
    def recommendation(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        
        return http.request.render("adm.template_application_menu_recommendation", {
            "application": application,
            "application_id": params["application_id"],
        })
    
    @http.route("/admission/applications/<int:application_id>/document-upload", auth="public", methods=["GET"], website=True, csrf=False)
    def document_upload(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        student_application = ApplicationEnv.browse([params["application_id"]])
        
        return http.request.render("adm.template_application_menu_upload_file", {
            "student_application": student_application,
            "application_id": params["application_id"],
        }) 
    
    @http.route("/admission/applications/<int:application_id>/electronic-signature", auth="public", methods=["GET"], website=True, csrf=False)
    def electronic_signature(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])
        
        return http.request.render("adm.template_application_menu_electronic_signature_page", {
            "application_id": params["application_id"],
            "application": application,
        })
    
    @http.route("/admission/applications/<int:application_id>/review", auth="public", methods=["GET"], website=True, csrf=False)
    def review(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
         
        student_application = ApplicationEnv.browse([params["application_id"]])
        application_status_ids = http.request.env["adm.application.status"].browse(http.request.env["adm.application.status"].search([]))
         
        return http.request.render("adm.template_application_menu_progress", {
            "student_application": student_application,
            "application_status_ids": application_status_ids.ids,
            "application_id": params["application_id"],
        }) 
    
