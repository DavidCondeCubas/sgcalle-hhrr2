odoo.define('payment_paguelofacil.payment_form', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Dialog = require('web.Dialog');
var PaymentForm = require('payment.payment_form');

var qweb = core.qweb;
var _t = core._t;

ajax.loadXML('/payment_paguelofacil/static/src/xml/paguelofacil_templates.xml', qweb);

PaymentForm.include({

/*     willStart: function () {
        return this._super.apply(this, arguments).then(function () {
            return ajax.loadJS("https://js.paguelofacil.com/v3/");
        })
    },
 */
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * called when clicking on pay now or add payment event to create token for credit card/debit card.
     *
     * @private
     * @param {Event} ev
     * @param {DOMElement} checkedRadio
     * @param {Boolean} addPmEvent
     */_createPaguelofacilToken: function (ev, $checkedRadio, addPmEvent) {
        var self = this;
        if (ev.type === 'submit') {
            var button = $(ev.target).find('*[type="submit"]')[0]
        } else {
            var button = ev.target;
        }
        this.disableButton(button);
        var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
        var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
        var inputsForm = $('input', acquirerForm);
        if (this.options.partnerId === undefined) {
            console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
        }

        var formData = self.getFormData(inputsForm);
        var paguelofacil = this.paguelofacil;
        var card = this.paguelofacil_card_element;
        //if (card._invalid) {
        //    return;
        //}
        return this._rpc({
            route: formData.data_set,
            params: formData,
        }).then(function(result) {
            if (addPmEvent) {
                if (formData.return_url) {
                    window.location = formData.return_url;
                } else {
                    window.location.reload();
                }
            } else {
                $checkedRadio.val(result.id);
                self.el.submit();
            }
        }).guardedCatch(function (error) {
            // We don't want to open the Error dialog since
            // we already have a container displaying the error
            if (error.event) {
                error.event.preventDefault();
            }
            // if the rpc fails, pretty obvious
            self.enableButton(button);
            self.displayError(
                _t('Unable to save card'),
                _t("We are not able to add your payment method at the moment. ") +
                    self._parseError(error)
            );
        });
    },
    /**
     * called when clicking a Paguelofacil radio if configured for s2s flow; instanciates the card and bind it to the widget.
     *
     * @private
     * @param {DOMElement} checkedRadio
     */
    _bindPaguelofacilCard: function ($checkedRadio) {
    //    var paguelofacil = Paguelofacil(formData.paguelofacil_api_key);
/*         var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
        var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
        var inputsForm = $('input', acquirerForm);
        var formData = this.getFormData(inputsForm);
        var element = paguelofacil.elements();
        var card = element.create('card', {hidePostalCode: true});
        card.mount('#card-element');
        card.on('ready', function(ev) {
            card.focus();
        });
        card.addEventListener('change', function (event) {
            var displayError = document.getElementById('card-errors');
            displayError.textContent = '';
            if (event.error) {
                displayError.textContent = event.error.message;
            }
        });
        this.paguelofacil = paguelofacil;
        this.paguelofacil_card_element = card; */
    },
    /**
     * destroys the card element and any paguelofacil instance linked to the widget.
     *
     * @private
     */
    _unbindPaguelofacilCard: function () {
        if (this.paguelofacil_card_element) {
            this.paguelofacil_card_element.destroy();
        }
        this.paguelofacil = undefined;
        this.paguelofacil_card_element = undefined;
    },
    /**
     * @override
     */
    updateNewPaymentDisplayStatus: function () {
        var $checkedRadio = this.$('input[type="radio"]:checked');

        if ($checkedRadio.length !== 1) {
            return;
        }
        var provider = $checkedRadio.data('provider')
        if (provider === 'paguelofacil') {
            // always re-init paguelofacil (in case of multiple acquirers for paguelofacil, make sure the paguelofacil instance is using the right key)
            this._unbindPaguelofacilCard();
            if (this.isNewPaymentRadio($checkedRadio)) {
                this._bindPaguelofacilCard($checkedRadio);
            }
        }
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    payEvent: function (ev) {
        ev.preventDefault();
        var $checkedRadio = this.$('input[type="radio"]:checked');

        // first we check that the user has selected a paguelofacil as s2s payment method
        if ($checkedRadio.length === 1 && this.isNewPaymentRadio($checkedRadio) && $checkedRadio.data('provider') === 'paguelofacil') {
            return this._createPaguelofacilToken(ev, $checkedRadio);
        } else {
            return this._super.apply(this, arguments);
        }
    },
    /**
     * @override
     */
    addPmEvent: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        var $checkedRadio = this.$('input[type="radio"]:checked');

        // first we check that the user has selected a paguelofacil as add payment method
        if ($checkedRadio.length === 1 && this.isNewPaymentRadio($checkedRadio) && $checkedRadio.data('provider') === 'paguelofacil') {
            return this._createPaguelofacilToken(ev, $checkedRadio, true);
        } else {
            return this._super.apply(this, arguments);
        }
    },
});
});
