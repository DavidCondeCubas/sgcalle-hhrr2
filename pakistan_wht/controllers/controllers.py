# -*- coding: utf-8 -*-
# from odoo import http


# class PakistanWht(http.Controller):
#     @http.route('/pakistan_wht/pakistan_wht/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pakistan_wht/pakistan_wht/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pakistan_wht.listing', {
#             'root': '/pakistan_wht/pakistan_wht',
#             'objects': http.request.env['pakistan_wht.pakistan_wht'].search([]),
#         })

#     @http.route('/pakistan_wht/pakistan_wht/objects/<model("pakistan_wht.pakistan_wht"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pakistan_wht.object', {
#             'object': obj
#         })
