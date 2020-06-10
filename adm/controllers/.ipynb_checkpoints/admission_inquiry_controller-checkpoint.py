# -*- coding: utf-8 -*-
from odoo import http
from ..utils import formatting
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    #===================================================================================================================
    # @http.route("/")
    # def
    #===================================================================================================================

    @http.route("/admission/inquiry", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        countries = http.request.env['res.country']
        states = http.request.env['res.country.state']
        contact_times = http.request.env['adm.contact_time']
        degree_programs = http.request.env['adm.degree_program']

        grade_level = http.request.env['school_base.grade_level']
        school_year = http.request.env['school_base.school_year']
        

        response = http.request.render('adm.template_admission_inquiry', {
            'grade_levels': grade_level.search([]),
            'school_years': school_year.search([]),
            'countries': countries.search([]),
            'states': states.search([]),
            'contact_times': contact_times.search([]),
            'degree_programs': degree_programs.search([]),
        })
        return response

    @http.route("/admission/inquiry", auth="public", methods=["POST"], website=True, csrf=False)
    def add_inquiry(self, **params):
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""
            
        PartnerEnv = http.request.env['res.partner']
        
        # Create a new family
        full_name = "{}, {}{}".format(params["txtLastName"], 
                                      params["txtFirstName"], 
                                      "" if not params["txtMiddleName"] else " {}".format(params["txtMiddleName"]))
        
        last_name = params["txtLastName"]
        street = params["txtStreetAddress"]
        # street2 = params["txtStreetAddress2"]
        country_id = int(params["selCountry"])
        state = int(params["selState"]) if params["selState"] else False
        zip = params["txtZip"]
        
        mobile = params["txtCellPhone"]
        phone = params["txtHomePhone"]
        email = params["txtEmail"]
        city = params["txtCity"]
        
        family_id = PartnerEnv.sudo().create({
            "name": "{} family".format(last_name),
            
            "company_type": "company",
            
            "street": street,
            "country_id": country_id,
            "state_id": state,
            "zip": zip,
            "city": city,
            
            'mobile': mobile,
            'phone': phone,
            'email': email,
        })
        
        parent_id = PartnerEnv.sudo().create({
            "name": full_name,
            
            "parent_id": family_id.id,
            "function": "parent",
            
            "street": street,
            "country_id": country_id,
            "state_id": state,
            "zip": zip,
            "city": city,
            
            'mobile': mobile,
            'phone': phone,
            'email': email,
        })
        
        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        grade_level_list = list(map(int, post_parameters().getlist("selStudentGradeLevel")))
        school_year_list = list(map(int, post_parameters().getlist("selStudentSchoolYear")))
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
             
            full_name_student = "{}, {}{}".format(last_name, first_name, "" if not middle_name else " {}".format(middle_name))
 
            id_student = PartnerEnv.sudo().create({
                "name": full_name_student,
                
                "parent_id": family_id.id,
                "function": "student",
                
                "street": street,
                "country_id": country_id,
                "state_id": state,
                "zip": zip,
                "city": city,
                
                'mobile': mobile,
                'phone': phone,
                'email': email,
            })
            
            # Create an inquiry for each new student
            new_inquiry = InquiryEnv.sudo().create({
                "partner_id": id_student.id,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'gender': http.request.env.ref('adm.{}'.format(gender)).id,
#                'birthday': birthday,
                
                'school_year_id': school_year,
                'grade_level_id': grade_level,
                'current_school': current_school,
#                'current_school_address': current_school_address,
                'responsible_id': parent_id.id
            })
            
            id_student.inquiry_id = new_inquiry.id
            
            id_students.append(id_student)
            
        response = http.request.render('adm.template_inquiry_sent')
        return response

