# -*- coding: utf-8 -*-
# from odoo import http


# class TransversalSubscriptions(http.Controller):
#     @http.route('/transversal_subscriptions/transversal_subscriptions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transversal_subscriptions/transversal_subscriptions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transversal_subscriptions.listing', {
#             'root': '/transversal_subscriptions/transversal_subscriptions',
#             'objects': http.request.env['transversal_subscriptions.transversal_subscriptions'].search([]),
#         })

#     @http.route('/transversal_subscriptions/transversal_subscriptions/objects/<model("transversal_subscriptions.transversal_subscriptions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transversal_subscriptions.object', {
#             'object': obj
#         })
