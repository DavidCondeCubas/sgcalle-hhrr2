# -*- coding: utf-8 -*-
# from odoo import http


# class SchoolFinance(http.Controller):
#     @http.route('/school_finance/school_finance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/school_finance/school_finance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('school_finance.listing', {
#             'root': '/school_finance/school_finance',
#             'objects': http.request.env['school_finance.school_finance'].search([]),
#         })

#     @http.route('/school_finance/school_finance/objects/<model("school_finance.school_finance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('school_finance.object', {
#             'object': obj
#         })
