# -*- coding: utf-8 -*-
import logging
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaguelofacilController(http.Controller):
    _success_url = '/payment/paguelofacil/success'
    _cancel_url = '/payment/paguelofacil/cancel'

    @http.route(['/payment/paguelofacil/success', '/payment/paguelofacil/cancel'], type='http', auth='public')
    def paguelofacil_success(self, **kwargs):
        request.env['payment.transaction'].sudo().form_feedback(kwargs, 'paguelofacil')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/paguelofacil/s2s/create_json_3ds'], type='json', auth='public', csrf=False)
    def paguelofacil_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        _logger.info("Testing")
        if not kwargs.get('partner_id'):
            kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
        token = request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).s2s_process(kwargs)

        if not token:
            res = {
                'result': False,
            }
            return res

        res = {
            'result': True,
            'id': token.id,
            'short_name': token.short_name,
            '3d_secure': False,
            'verified': False,
        }

        if verify_validity != False:
            token.validate()
            res['verified'] = token.verified

        return res

    @http.route('/payment/paguelofacil/s2s/auth', type='json', auth='public', csrf=False)
    def paguelofacil_s2s_create_setup_intent(self, acquirer_id, **kwargs):
        acquirer = request.env['payment.acquirer'].browse(int(acquirer_id))
        res = acquirer._create_paguelofacil_res_auth(kwargs)
        return res.get('client_secret')

    @http.route('/payment/paguelofacil/s2s/process_payment_intent', type='json', auth='public', csrf=False)
    def paguelofacil_s2s_process_payment_intent(self, **post):
        return request.env['payment.transaction'].sudo().form_feedback(post, 'paguelofacil')
