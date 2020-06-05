# -*- coding: utf-8 -*-
# from odoo import http


# class HrExtends(http.Controller):
#     @http.route('/hr_extends/hr_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_extends/hr_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_extends.listing', {
#             'root': '/hr_extends/hr_extends',
#             'objects': http.request.env['hr_extends.hr_extends'].search([]),
#         })

#     @http.route('/hr_extends/hr_extends/objects/<model("hr_extends.hr_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_extends.object', {
#             'object': obj
#         })
