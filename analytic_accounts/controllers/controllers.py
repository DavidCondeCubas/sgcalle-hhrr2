# -*- coding: utf-8 -*-
from odoo import http

# class Addons/schoolAnalyticAccounts(http.Controller):
#     @http.route('/addons/analytic_accounts/addons/analytic_accounts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/addons/analytic_accounts/addons/analytic_accounts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('addons/analytic_accounts.listing', {
#             'root': '/addons/analytic_accounts/addons/analytic_accounts',
#             'objects': http.request.env['addons/analytic_accounts.addons/analytic_accounts'].search([]),
#         })

#     @http.route('/addons/analytic_accounts/addons/analytic_accounts/objects/<model("addons/analytic_accounts.addons/analytic_accounts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('addons/analytic_accounts.object', {
#             'object': obj
#         })