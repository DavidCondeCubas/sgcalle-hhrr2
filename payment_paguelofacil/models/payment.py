# coding: utf-8

import logging
import requests
import pprint
import json
import hashlib
from requests.exceptions import HTTPError
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

from odoo.addons.payment.models.payment_acquirer import ValidationError
from ..controllers.main import PaguelofacilController

_logger = logging.getLogger(__name__)

INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYG', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
]

def get_partner_address(partner_id):

    street  = (partner_id.street + ",") if partner_id.street else ""
    city    = (partner_id.city + ",") if partner_id.city else ""
    state   = (partner_id.state_id.name + ",") if partner_id.state_id else ""
    country = (partner_id.conutry_id.name + ",") if partner_id.country_id else ""

    return f"{street} {city} {state} {country}".strip().rstrip(",")

class PaymentAcquirerPaguelofacil(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paguelofacil', 'Paguelofacil')])
    
    paguelofacil_cclw = fields.Char(required_if_provider='paguelofacil', groups='base.group_user')
    paguelofacil_api_key = fields.Char(required_if_provider='paguelofacil', groups='base.group_user')
    paguelofacil_save_card = fields.Boolean("Save Card")
    paguelofacil_image_url = fields.Char(
        "Checkout Image URL", groups='base.group_user',
        help="A relative or absolute URL pointing to a square image of your "
             "brand or product. As defined in your Paguelofacil profile. See: "
             "https://paguelofacil.com/docs/checkout")

    def paguelofacil_form_generate_values(self, tx_values):
        self.ensure_one()

        base_url = self.get_base_url()
        paguelofacil_session_data = {
            'payment_method_types[]': 'card',
            'line_items[][amount]': int(tx_values['amount'] if tx_values['currency'].name in INT_CURRENCIES else float_round(tx_values['amount'] * 100, 2)),
            'line_items[][currency]': tx_values['currency'].name,
            'line_items[][quantity]': 1,
            'line_items[][name]': tx_values['reference'],
            'client_reference_id': tx_values['reference'],
            'success_url': urls.url_join(base_url, PaguelofacilController._success_url) + '?reference=%s' % tx_values['reference'],
            'cancel_url': urls.url_join(base_url, PaguelofacilController._cancel_url) + '?reference=%s' % tx_values['reference'],
            'payment_intent_data[description]': tx_values['reference'],
            'customer_email': tx_values.get('partner_email') or tx_values.get('billing_partner_email'),
        }
        #tx_values['session_id'] = self._create_paguelofacil_session(paguelofacil_session_data)

        return tx_values

    def _get_api_key(self):
        API_KEY_TESTING = "WT5hTaUcpa4J3h4AmrZa2EXXJs8boUVa|DIRd852djHbq2j5Fca5VDUkDbExTBCVf"
        return API_KEY_TESTING if self.state == 'test' else self.sudo().paguelofacil_api_key

    def _paguelofacil_request(self, url, data={}, method='POST'):
        self.ensure_one()
        url = urls.url_join(self._get_paguelofacil_api_url(), url)
        headers = {
            'AUTHORIZATION': '%s' % self.sudo()._get_api_key(),
            'content-type': "application/json"
        }
        data_json = json.dumps(data)
        resp = requests.request(method, url, data=data_json, headers=headers)

        # Paguelofacil send us 200 code, but with a success variable if the request cannot be processed.
        resp_json = resp.json()
        if not resp_json.get("success", False):

            error_desc = resp_json.get("headerStatus", {}).get("description", "")
            resp_msg = resp_json.get("message", "")

            error_msg = " " + (_("Paguelofacil gave us the following info about the problem, description: '%s', message: '%s'") % (error_desc, resp_msg))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return resp_json


    def _create_paguelofacil_res_auth(self, kwargs):
        self.ensure_one()
        params = {
            'usage': 'off_session',
        }
        _logger.info('_paguelofacil_auth: Sending values to paguelofacil, values:\n%s', pprint.pformat(params))

        res = self._paguelofacil_request('/rest/processTx/AUTH', params)

        _logger.info('_paguelofacil_auth: Values received:\n%s', pprint.pformat(res))
        return res

    @api.model
    def _get_paguelofacil_api_url(self):
        return 'https://sandbox.paguelofacil.com/' if self.state == 'test' else 'https://secure.paguelofacil.com/'

    def _get_cclw(self):
        return "D17B05A095489D1176560B4666A283454185F353F401D0201CC5C16F92535DF6B1DEBA18E79442CC0D6F75FD024207680AFBDFD6CF015478BF30CBEF9160A08D" \
                if self.state == "test" else self.paguelofacil_cclw

    def paguelofacil_get_form_action_url(self, values={}):
        return self._get_paguelofacil_api_url() + 'LinkDeamon.cfm'

    def _build_res_json_auth(self, values):
        return {
            "cclw": self._get_cclw(),
            "amount": values["amount"],
            "taxAmount": 0.0,#, values["tax_amount"],
            "email": values["email"],
            "phone": values["phone"],
            "address": values["address"],
            "concept": values["description"],
            "description": values["description"],
            "cardInformation": {
                "cardNumber": values["card_number"],
                "expMonth": values["exp_month"],
                "expYear": values["exp_year"],
                "cvv": values["cvv"],
                "firstName": values["first_name"],
                "lastName": values["last_name"],
            }
        }

    @api.model
    def paguelofacil_s2s_form_process(self, data):
        # We need to create a AUTH to get a token number
        acquirer_id = self.env['payment.acquirer'].browse(int(data['acquirer_id']))
        SequenceEnv = self.env["ir.sequence"]
        next_tax_amount = float(SequenceEnv.next_by_code("paguelofacil.sequence"))
        pm = data.get('payment_method')

        # Partner information
        email = data["pf_card_email"]
        phone = data["pf_card_phone"]
        address = data["pf_card_address"]
        description = "Auth for tokenization"

        # Payment information
        amount = data["amount"]
        card_number = data["pf_card_number"]
        exp_month   = data["pf_card_month"]
        exp_year    = data["pf_card_year"]
        cvv         = data["pf_card_cvv"]

        first_name = data["pf_card_name"]
        last_name  = data["pf_card_lastname"]

        dict_auth = {
            "email": email,
            "amount": amount,
            "phone": phone,
            "address": address,
            "description": description,
            "card_number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvv": cvv,
            "first_name": first_name,
            "last_name": last_name,
            "tax_amount": next_tax_amount,
        }

        auth_sending_json = self._build_res_json_auth(dict_auth)

        #url = "/rest/ccprocessing"
        #url = '/rest/processTx/AUTH'
        url = '/rest/processTx/AUTH_CAPTURE'
        auth_json = acquirer_id._paguelofacil_request(url, data=auth_sending_json, method='POST')

        auth_data = auth_json["data"]
        if auth_data["status"] == 1:
            private_card = '*' * (len(card_number)-4) + card_number[-4:]
            payment_token = self.env['payment.token'].sudo().create({

                'acquirer_id': int(data['acquirer_id']),
                'partner_id':  int(data['partner_id']),
                'idtx':        auth_data.get("idtx"),
                'name':        private_card,

                'paguelofacil_email': email,
                'paguelofacil_phone': phone,
                'paguelofacil_address': address,

                'acquirer_ref': auth_data.get("codOper"),
                'is_auth_caputure': True,
                'auth_json': json.dumps(auth_json)
            })
        else:
            debug_error_desc = auth_json.get("headerStatus", {}).get("description", "")
            resp_msg = auth_data.get("messageSys", "")

            debug_error_msg = " " + (_("Paguelofacil gave us the following info about the problem, description: '%s', message: '%s'") % (debug_error_desc, resp_msg))
           
            _logger.error(debug_error_msg)
            raise ValidationError(resp_msg)
        return payment_token

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirerPaguelofacil, self)._get_feature_support()
        res['tokenize'].append('paguelofacil')
        return res



class PaymentTransactionPaguelofacil(models.Model):
    _inherit = 'payment.transaction'

    paguelofacil_cod_oper = fields.Char("Paguelofacil cod oper")

    paguelofacil_return_url = fields.Char("Paguelofacil return url")
    paguelofacil_cod_oper   = fields.Char("Paguelofacil cod oper")
    paguelofacil_related_tx = fields.Char("Paguelofacil related tx")

    paguelofacil_email   = fields.Char()
    paguelofacil_phone   = fields.Char()
    paguelofacil_address = fields.Char()

    paguelofacil_cod_oper = fields.Char()


    def _get_processing_info(self):
        res = super()._get_processing_info()
        if self.acquirer_id.provider == 'paguelofacil':
            paguelofacil_info = {
                'paguelofacil_return_url': self.paguelofacil_return_url,
                'paguelofacil_cod_oper': self.paguelofacil_cod_oper,
                'paguelofacil_api_key': self.acquirer_id.paguelofacil_api_key,
            }
            res.update(paguelofacil_info)
        return res

    def form_feedback(self, data, acquirer_name):
        if data.get('reference') and acquirer_name == 'paguelofacil':
            transaction = self.env['payment.transaction'].search([('reference', '=', data['reference'])])

            url = 'payment_intents/%s' % transaction.paguelofacil_payment_intent
            resp = transaction.acquirer_id._paguelofacil_request(url)
            if resp.get('charges') and resp.get('charges').get('total_count'):
                resp = resp.get('charges').get('data')[0]

            data.update(resp)
            _logger.info('Paguelofacil: entering form_feedback with post data %s' % pprint.pformat(data))
        return super(PaymentTransactionPaguelofacil, self).form_feedback(data, acquirer_name)

    def _paguelofacil_create_payment_intent(self, acquirer_ref=None, email=None):
        SequenceEnv = self.env["ir.sequence"]
        token_id = self.payment_token_id
        acquirer_id = self.acquirer_id
        res = {}

        if token_id.is_auth_caputure:
            res = json.loads(token_id.auth_json)
            token_id.write({
                "is_auth_caputure": False,
                "auth_json": "",
            })
        else:
            next_tax_amount = float(SequenceEnv.next_by_code("paguelofacil.sequence"))

            charge_params = {
                'cclw': self.acquirer_id._get_cclw(),
                'taxAmount': 0.0, #next_tax_amount,
                'codOper': acquirer_ref,

                'amount': self.amount,
                "concept": (_("Payment in %s")) % self.acquirer_id.company_id.name,
                "description": self.reference,
                
                #'name': self.payment_token_id.paguelofacil_name,
                'email': self.payment_token_id.paguelofacil_email,
                'phone': self.payment_token_id.paguelofacil_phone,
                'address': self.payment_token_id.paguelofacil_address,
            }
            _logger.info('_paguelofacil_create_payment_intent: Sending values to paguelofacil, values:\n%s', pprint.pformat(charge_params))

            url = "/rest/processTx/RECURRENT"
            res = self.acquirer_id._paguelofacil_request(url, data=charge_params)


        self.acquirer_reference = res["data"]["codOper"]
        _logger.info('_paguelofacil_create_payment_intent: Values received:\n%s', pprint.pformat(res))
        if not acquirer_id.paguelofacil_save_card:
            token_id.sudo().active = False

        return res

    def paguelofacil_s2s_do_transaction(self, **kwargs):
        self.ensure_one()
        result = self._paguelofacil_create_payment_intent(acquirer_ref=self.payment_token_id.acquirer_ref, email=self.partner_email)
        return self._paguelofacil_s2s_validate_tree(result)

    def _create_paguelofacil_refund(self):

        refund_params = {
            'charge': self.acquirer_reference,
            'amount': int(float_round(self.amount * 100, 2)), # by default, paguelofacil refund the full amount (we don't really need to specify the value)
            'metadata[reference]': self.reference,
        }

        _logger.info('_create_paguelofacil_refund: Sending values to paguelofacil URL, values:\n%s', pprint.pformat(refund_params))
        res = self.acquirer_id._paguelofacil_request('refunds', refund_params)
        _logger.info('_create_paguelofacil_refund: Values received:\n%s', pprint.pformat(res))

        return res

    def paguelofacil_s2s_do_refund(self, **kwargs):
        self.ensure_one()
        result = self._create_paguelofacil_refund()
        return self._paguelofacil_s2s_validate_tree(result)

    @api.model
    def _paguelofacil_form_get_tx_from_data(self, data):
        """ Given a data dict coming from paguelofacil, verify it and find the related
        transaction record. """
        reference = data.get('reference')
        if not reference:
            paguelofacil_error = data.get('error', {}).get('message', '')
            _logger.error('Paguelofacil: invalid reply received from paguelofacil API, looks like '
                          'the transaction failed. (error: %s)', paguelofacil_error or 'n/a')
            error_msg = _("We're sorry to report that the transaction has failed.")
            if paguelofacil_error:
                error_msg += " " + (_("Paguelofacil gave us the following info about the problem: '%s'") %
                                    paguelofacil_error)
            error_msg += " " + _("Perhaps the problem can be solved by double-checking your "
                                 "credit card details, or contacting your bank?")
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx:
            error_msg = (_('Paguelofacil: no order found for reference %s') % reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = (_('Paguelofacil: %s orders found for reference %s') % (len(tx), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    def _paguelofacil_s2s_validate_tree(self, tree):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info('Paguelofacil: trying to validate an already validated tx (ref %s)', self.reference)
            return True

        payment_data = tree.get("data")
        status = payment_data.get("status")
        tx_id = payment_data.get("idtx")
        vals = {
            "date": fields.datetime.now(),
            "acquirer_reference": tx_id,
            "paguelofacil_return_url": payment_data.get("return_url"),
            "paguelofacil_cod_oper": payment_data.get("codOper"),
            "paguelofacil_related_tx": payment_data.get("relatedTx"),
        }
        if status == 1:
            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            if self.type == 'form_save':
                s2s_data = {
                    'customer': tree.get('customer'),
                    'payment_method': tree.get('payment_method'),
                    'card': tree.get('payment_method_details').get('card'),
                    'acquirer_id': self.acquirer_id.id,
                    'partner_id': self.partner_id.id
                }
                token = self.acquirer_id.paguelofacil_s2s_form_process(s2s_data)
                self.payment_token_id = token.id
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        else:
            error = tree.get("failure_message") or tree.get('error', {}).get('message')
            self._set_transaction_error(error)
            return False

    def _paguelofacil_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if data.get('amount') != int(self.amount if self.currency_id.name in INT_CURRENCIES else float_round(self.amount * 100, 2)):
            invalid_parameters.append(('Amount', data.get('amount'), self.amount * 100))
        if data.get('currency').upper() != self.currency_id.name:
            invalid_parameters.append(('Currency', data.get('currency'), self.currency_id.name))
        if data.get('payment_intent') and data.get('payment_intent') != self.paguelofacil_payment_intent:
            invalid_parameters.append(('Payment Intent', data.get('payment_intent'), self.paguelofacil_payment_intent))
        return invalid_parameters

    def _paguelofacil_form_validate(self, data):
        return self._paguelofacil_s2s_validate_tree(data)


class PaymentTokenPaguelofacil(models.Model):
    _inherit = 'payment.token'

    paguelofacil_email   = fields.Char()
    paguelofacil_phone   = fields.Char()
    paguelofacil_address = fields.Char()
    is_auth_caputure     = fields.Boolean()
    auth_json            = fields.Char()

    @api.model
    def paguelofacil_create(self, values):
        #if values.get('paguelofacil_payment_method') and not values.get('acquirer_ref'):
        #   partner_id = self.env['res.partner'].browse(values.get('partner_id'))
        #   payment_acquirer = self.env['payment.acquirer'].browse(values.get('acquirer_id'))

         #   # create customer to stipe
        #    customer_data = {
        #        'email': partner_id.email
        #    }
        #    cust_resp = payment_acquirer._paguelofacil_request('customers', customer_data)
#
 #           # link customer with payment method
 #           api_url_payment_method = 'payment_methods/%s/attach' % values['paguelofacil_payment_method']
 #           method_data = {
 #               'customer': cust_resp.get('id')
 #           }
 #           payment_acquirer._paguelofacil_request(api_url_payment_method, method_data)
 #           return {
 #               'acquirer_ref': cust_resp['id'],
 #           } """
        return values

    def _paguelofacil_sca_migrate_customer(self):
        """Migrate a token from the old implementation of Paguelofacil to the SCA one.

        In the old implementation, it was possible to create a valid charge just by
        giving the customer ref to ask Paguelofacil to use the default source (= default
        card). Since we have a one-to-one matching between a saved card, this used to
        work well - but now we need to specify the payment method for each call and so
        we have to contact paguelofacil to get the default source for the customer and save it
        in the payment token.
        This conversion will happen once per token, the first time it gets used following
        the installation of the module."""
        self.ensure_one()
        url = "customers/%s" % (self.acquirer_ref)
        data = self.acquirer_id._paguelofacil_request(url, method="GET")
        sources = data.get('sources', {}).get('data', [])
        pm_ref = False
        if sources:
            if len(sources) > 1:
                _logger.warning('paguelofacil sca customer conversion: there should be a single saved source per customer!')
            pm_ref = sources[0].get('id')
        else:
            url = 'payment_methods'
            params = {
                'type': 'card',
                'customer': self.acquirer_ref,
            }
            payment_methods = self.acquirer_id._paguelofacil_request(url, params, method='GET')
            cards = payment_methods.get('data', [])
            if len(cards) > 1:
                _logger.warning('paguelofacil sca customer conversion: there should be a single saved source per customer!')
            pm_ref = cards and cards[0].get('id')
        if not pm_ref:
            raise ValidationError(_('Unable to convert Paguelofacil customer for SCA compatibility. Is there at least one card for this customer in the Paguelofacil backend?'))
        self.paguelofacil_payment_method = pm_ref
        _logger.info('converted old customer ref to sca-compatible record for payment token %s', self.id)
