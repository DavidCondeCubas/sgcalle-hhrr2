# -*- coding: utf-8 -*-
{
    'name': "Human resources extension",

    'summary': """ Human Resource module extensions """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human resources',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', "hr", "hr_contract"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'data/employee_types.xml',
    ],
}
