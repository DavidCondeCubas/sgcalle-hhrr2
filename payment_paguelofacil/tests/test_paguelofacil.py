# -*- coding: utf-8 -*-
import odoo
from odoo import fields
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tools import mute_logger


class PaguelofacilCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(PaguelofacilCommon, self).setUp()
        self.paguelofacil = self.env.ref('payment.payment_acquirer_paguelofacil')
        self.paguelofacil.write({
            'paguelofacil_cclw': 'D17B05A095489D1176560B4666A283454185F353F401D0201CC5C16F92535DF6B1DEBA18E79442CC0D6F75FD024207680AFBDFD6CF015478BF30CBEF9160A08D',
            'paguelofacil_api_key': 'WT5hTaUcpa4J3h4AmrZa2EXXJs8boUVa|DIRd852djHbq2j5Fca5VDUkDbExTBCVf',
            'state': 'test',
        })
        self.token = self.env['payment.token'].create({
            'name': 'Test Card',
            'acquirer_id': self.paguelofacil.id,
            'acquirer_ref': 'cus_G27S7FqQ2w3fuH',
            'paguelofacil_payment_method': 'pm_1FW3DdAlCFm536g8eQoSCejY',
            'partner_id': self.buyer.id,
            'verified': True,
        })


@odoo.tests.tagged('post_install', '-at_install', '-standard', 'external')
class PaguelofacilTest(PaguelofacilCommon):

    def test_10_paguelofacil_s2s(self):
        self.assertEqual(self.paguelofacil.state, 'test', 'test without test environment')
        # Create transaction
        tx = self.env['payment.transaction'].create({
            'reference': 'paguelofacil_test_10_%s' % fields.datetime.now().strftime('%Y%m%d_%H%M%S'),
            'currency_id': self.currency_euro.id,
            'acquirer_id': self.paguelofacil.id,
            'partner_id': self.buyer_id,
            'payment_token_id': self.token.id,
            'type': 'server2server',
            'amount': 115.0
        })
        tx.with_context(off_session=True).paguelofacil_rest_do_transaction()

        # Check state
        self.assertEqual(tx.state, 'done', 'Paguelofacil: Transcation has been discarded.')

    def test_20_paguelofacil_form_render(self):
        self.assertEqual(self.paguelofacil.state, 'test', 'test without test environment')

        # ----------------------------------------
        # Test: button direct rendering
        # ----------------------------------------

        # render the button
        self.paguelofacil.render('SO404', 320.0, self.currency_euro.id, values=self.buyer_values).decode('utf-8')

    def test_30_paguelofacil_form_management(self):
        self.assertEqual(self.paguelofacil.state, 'test', 'test without test environment')
        ref = 'paguelofacil_test_30_%s' % fields.datetime.now().strftime('%Y%m%d_%H%M%S')
        tx = self.env['payment.transaction'].create({
            'amount': 4700.0,
            'acquirer_id': self.paguelofacil.id,
            'currency_id': self.currency_euro.id,
            'reference': ref,
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_france.id,
            'payment_token_id': self.token.id,
        })
        res = tx.with_context(off_session=True)._paguelofacil_create_payment_intent()
        tx.paguelofacil_payment_intent = res.get('payment_intent')

        # typical data posted by Paguelofacil after client has successfully paid
        paguelofacil_post_data = {'reference': ref}
        # validate it
        tx.form_feedback(paguelofacil_post_data, 'paguelofacil')
        self.assertEqual(tx.state, 'done', 'Paguelofacil: validation did not put tx into done state')
        self.assertEqual(tx.acquirer_reference, paguelofacil_post_data.get('id'), 'Paguelofacil: validation did not update tx id')
