odoo.define('payment_paguelofacil.processing', function (require) {
'use strict';

var ajax = require('web.ajax');
var rpc = require('web.rpc')
var publicWidget = require('web.public.widget');

var PaymentProcessing = publicWidget.registry.PaymentProcessing;

return PaymentProcessing.include({
    init: function () {
        this._super.apply(this, arguments);
        this._authInProgress = false;
    },
/*     willStart: function () {
        return this._super.apply(this, arguments).then(function () {
            return ajax.loadJS("https://js.paguelofacil.com/v3/");
        })
    }, */
    _paguelofacilAuthenticate: function (tx) {
        var paguelofacil = Paguelofacil(tx.paguelofacil_api_key);
        return paguelofacil.handleCardPayment(tx.paguelofacil_payment_intent_secret)
        .then(function(result) {
            if (result.error) {
                return Promise.reject({"message": {"data": { "message": result.error.message}}});
            }
            return rpc.query({
                route: '/payment/paguelofacil/s2s/process_payment_intent',
                params: _.extend({}, result.paymentIntent, {reference: tx.reference}),
            });
        }).then(function() {
            window.location = '/payment/process';
        }).guardedCatch(function () {
            this._authInProgress = false;
        });
    },
    processPolledData: function(transactions) {
        this._super.apply(this, arguments);
        for (var itx=0; itx < transactions.length; itx++) {
            var tx = transactions[itx];
            if (tx.acquirer_provider === 'paguelofacil' && tx.state === 'pending' && tx.paguelofacil_payment_intent_secret && !this._authInProgress) {
                this._authInProgress = true;
                this._paguelofacilAuthenticate(tx);
            }
        }
    },
});
});