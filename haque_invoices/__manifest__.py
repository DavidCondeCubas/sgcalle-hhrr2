# -*- coding: utf-8 -*-
{
    'name': "Haque Invoices",

    'summary': """ Allow you make honduras invoices """,

    'description': """
        Honduras Invoices and Reports, this add min and max invoice number,
        issue limit date.
    """,

    'author': "EduwebGroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'account',
        'sale',
        'product',
        'account_reports',
        'barcodes',
        'school_finance'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/reports.xml',
        'views/views.xml',
        'views/templates.xml',
    ]
}
