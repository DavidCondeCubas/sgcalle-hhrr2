odoo.define('payment_paguelofacil.paguelofacil', function (require) {
"use strict";

console.error("Error Paguelofacil")
window.location.href = "https://secure.paguelofacil.com/LinkDeamon.cfm?CCLW=F2379F9DA66C5C56B601B6ADF421692A9E35685B94901BF9AD7A719E3F75C93DB880ABF39ED5E510A896B6B92ACBA0CD3934EC931A7B0A49E34591C62B97076E&CMTN=0.00&CDSC=Testing"

var ajax = require('web.ajax');
var core = require('web.core');

var qweb = core.qweb;
var _t = core._t;

ajax.loadXML('/payment_stripe/static/src/xml/stripe_templates.xml', qweb);

if ($.blockUI) {
    // our message needs to appear above the modal dialog
    $.blockUI.defaults.baseZ = 2147483647; //same z-index as StripeCheckout
    $.blockUI.defaults.css.border = '0';
    $.blockUI.defaults.css["background-color"] = '';
    $.blockUI.defaults.overlayCSS["opacity"] = '0.9';
}

require('web.dom_ready');
if (!$('.o_payment_form').length) {
    return Promise.reject("DOM doesn't contain '.o_payment_form'");
}

var observer = new MutationObserver(function (mutations, observer) {
    for (var i = 0; i < mutations.length; ++i) {
        for (var j = 0; j < mutations[i].addedNodes.length; ++j) {
            if (mutations[i].addedNodes[j].tagName.toLowerCase() === "form" && mutations[i].addedNodes[j].getAttribute('provider') === 'paguelofacil') {
                _redirectToPaguelofacilCheckout($(mutations[i].addedNodes[j]));
            }
        }
    }
});

function displayError(message) {
    var wizard = $(qweb.render('paguelofacil.error', {'msg': message || _t('Payment error')}));
    wizard.appendTo($('body')).modal({'keyboard': true});
    if ($.blockUI) {
        $.unblockUI();
    }
    $("#o_payment_form_pay").removeAttr('disabled');
}


function _redirectToPaguelofacilCheckout(providerForm) {
    // Open Checkout with further options
    if ($.blockUI) {
        var msg = _t("Just one more second, We are redirecting you to Stripe...");
        $.blockUI({
            'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                    '    <br />' + msg +
                    '</h2>'
        });
    }

    var paymentForm = $('.o_payment_form');
    if (!paymentForm.find('i').length) {
        paymentForm.append('<i class="fa fa-spinner fa-spin"/>');
        paymentForm.attr('disabled', 'disabled');
    }

    var _getStripeInputValue = function (name) {
        return providerForm.find('input[name="' + name + '"]').val();
    };

    var stripe = Stripe(_getStripeInputValue('stripe_key'));

    stripe.redirectToCheckout({
        sessionId: _getStripeInputValue('session_id')
    }).then(function (result) {
        if (result.error) {
            displayError(result.error.message);
        }
    });
}

$.getScript("https://js.stripe.com/v3/", function (data, textStatus, jqxhr) {
    observer.observe(document.body, {childList: true});
    _redirectToPaguelofacilCheckout($('form[provider="stripe"]'));
});
});
