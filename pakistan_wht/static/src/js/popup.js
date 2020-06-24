odoo.define('pakistan_wht.popup', function(require) {
    var FormController = require('web.FormController');
    var Dialog = require('web.Dialog');

    var ExtendFormController = FormController.include({
        _check_for_wht: function(res){

            let accepted_modules = ["purchase.order", "sale.order"]

            if (accepted_modules.indexOf(this.modelName) !== -1) {
                res.then(function() {
                    //self.do_notify('title', 'message');
                    // you can call a method on the server like this
                    self._rpc({
                        model: self.modelName,
                        method: 'search_read',
                        domain: [
                            ["id", "=", self.getSelectedIds()[0]]
                        ],
                        fields: ['name', "accumulated_amount", "partner_yearly_wht_forecast_amount", "exempt_upto", "exempt_upto_tax_percent", "partner_id"],
                        context: self.context,
                    }).then(function(result) {
                        result.forEach(function(order) {
                            if (order.partner_yearly_wht_forecast_amount <= 0 && parseInt(order.exempt_upto) > 0 &&
                                parseInt(order.exempt_upto_tax_percent) > 0 && order.accumulated_amount >= order.exempt_upto) {

                                let parter_name = order.partner_id[1];

                                var msm = parter_name + " should have taxes of " + order.exempt_upto_tax_percent + "%";

                                Dialog.alert(self, msm, {
                                    title: "Partner Taxes!"
                                });
                            }
                        });
                    })
                });
            }
        },
        createRecord: function() {
            let res = this._super.apply(this, arguments);
            this._check_for_wht(res);
            return res;
        },
        saveRecord: function() {
            let res = this._super.apply(this, arguments);
            this._check_for_wht(res);
            // if (this.modelName == 'purchase.order') {
            //     var self = this;
            //     res.then(function(changedFields) {
            //         console.log(changedFields);
            //         console.log(self.modelName);
            //         //self.do_notify('title', 'message');
            //         // you can call a method on the server like this
            //         self._rpc({
            //             model: self.modelName,
            //             method: 'search_read',
            //             domain: [
            //                 ["id", "=", self.getSelectedIds()[0]]
            //             ],
            //             fields: ['name', "accumulated_amount", "partner_yearly_wht_forecast_amount", "exempt_upto", "exempt_upto_tax_percent", "partner_id"],
            //             context: self.context,
            //         }).then(function(result) {
            //             result.forEach(function(purchase) {
            //                 if (purchase.partner_yearly_wht_forecast_amount <= 0 && parseInt(purchase.exempt_upto) > 0 &&
            //                     parseInt(purchase.exempt_upto_tax_percent) != 0 && purchase.accumulated_amount >= purchase.exempt_upto) {
            //                     var msm = purchase.partner_id[1] + " should have taxes of " + purchase.exempt_upto_tax_percent + "%";
            //                     Dialog.alert(self, msm, {
            //                         title: "Vendor Taxes!"
            //                     });
            //                 }
            //             });
            //         })
            //     });
            // }
            return res;
        }
    });
})