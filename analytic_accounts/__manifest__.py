# -*- coding: utf-8 -*-
{
    'name': "Analytic Accounts Improved",

    'summary': """ An improvement in Analyitic Accounts,
    by adding Graphics, filter, import/export automation and
    reports """,

    'description': """ An improvement in Analyitic Accounts,
    by adding Graphics, filter, import/export automation and
    reports """,

    'author': "Eduweb group",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1.2',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant', 'account_budget'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        "views/analytic_account_views.xml",
        "views/analytic_groups_views.xml",
        "views/account_analytic_group_view.xml",
        "data/reports.xml",
        "data/data_menu.xml",
    ],
}