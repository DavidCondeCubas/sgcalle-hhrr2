# -*- coding: utf-8 -*-
{
    'name': "Qatar Invoices",

    'summary': """ Qatar Invoices """,

    'description': """ Qatar invoice in purchase """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.6.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'purchase',
        "hr"
    ],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/reports.xml',
    ],
}
