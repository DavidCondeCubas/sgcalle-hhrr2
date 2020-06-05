# -*- coding: utf-8 -*-

{
    'name': "Admission School",

    'summary': """""",

    'description': """""",

    'author': "Eduweb Group SL",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'school_base', 'mail', 'website', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inherited_views.xml',
        'views/views_inquiry.xml',
        'views/views_application.xml',
        'views/configuration.xml',
        
        'data/menudata.xml',
        'data/sequences_data.xml',
        'data/statics_data.xml',
        'data/email_template_data.xml',
        'data/language_types.xml',
        'data/status_type_data.xml',
        'data/gender_data.xml',
        
        'views/web/template_application_list.xml',
        'views/web/template_inquiry_form.xml',
        'views/web/template_application_first_form.xml',

        'views/web/menu/template_application_menu.xml',
        'views/web/menu/template_application_menu_admissions_policy_agreement.xml',
        'views/web/menu/template_application_menu_alumni_currently_enrolled_students.xml',
        'views/web/menu/template_application_menu_electronic_signature_page.xml',
        'views/web/menu/template_application_menu_family_info.xml',
        'views/web/menu/template_application_menu_household1.xml',
        'views/web/menu/template_application_menu_household2.xml',
        'views/web/menu/template_application_menu_info.xml',
        'views/web/menu/template_application_menu_institutional_fee_declaration.xml',
        'views/web/menu/template_application_menu_instructions.xml',
        'views/web/menu/template_application_menu_medical_info.xml',
        'views/web/menu/template_application_menu_previous_school.xml',
        'views/web/menu/template_application_menu_progress.xml',
        'views/web/menu/template_application_menu_recommendation.xml',
        'views/web/menu/template_application_menu_references.xml',
        'views/web/menu/template_application_menu_house_address.xml',
        'views/web/menu/template_application_menu_student_info.xml',
        'views/web/menu/template_application_menu_upload_file.xml',
        
    ],
    'application': True
}

