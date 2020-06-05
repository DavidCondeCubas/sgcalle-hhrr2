odoo.define('register_payments.pos_view', function(require) {
    "use strict";

    var screens = require("point_of_sale.screens")
    var PopupWidget = require('point_of_sale.popups');
    var gui = require("point_of_sale.gui")
    var core = require("web.core")
    var QWeb = core.qweb;

    // Payment
    var BtnRegisterPayment = screens.ActionButtonWidget.extend({
        template: "BtnRegisterPayment",

        button_click: function() {
            var self = this;
            this.gui.show_screen("invoice_list")
        },

        clear_button_fun: function() {
            var order = this.pos.get_order();
            order.remove_orderline(order.get_selected_orderline());
        }
    });

    screens.define_action_button({ 'name': 'clear_button_fun', 'widget': BtnRegisterPayment });

    // Invoices 
    var BtnInvoices = screens.ActionButtonWidget.extend({
        template: "BtnInvoices",

        button_click: function() {
            var self = this;
            self.gui.show_screen("invoice_list")
        },

        got_to_invoices: function() {
            var order = this.pos.get_order();
            order.remove_orderline(order.get_selected_orderline());
        }
    });

    screens.define_action_button({ 'name': 'got_to_invoices', 'widget': BtnInvoices });

    // Invoices screeen
    var PosInvoiceScreenWidget = screens.ScreenWidget.extend({
        template: 'InvoicesLineWidget',
        back_screen: 'product',
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
        },

        show: function() {
            this._super();

            var today = new Date();

            var year = today.getFullYear();
            var month = ("0" + today.getMonth()).slice(-2);
            var day = ("0" + today.getDate()).slice(-2);

            var str_today = year + "-" + month + "-" + day;

            // "['&amp;', ('invoice_date_due', '&lt;', time.strftime('%Y-%m-%d')), ('state', '=', 'posted'), ('invoice_payment_state', '=', 'not_paid')]"
            this._rpc({
                model: "account.move",
                method: "search_read",
                args: [
                    [
                        ['invoice_date_due', '<', str_today],
                        ['state', '=', 'posted'],
                        ['invoice_payment_state', '=', 'not_paid']
                    ],
                    ["name", "invoice_date_due", "partner_id"]
                ]
            }).then(this.print_invoices.bind(this));
        },

        print_invoices: function(invoice) {
            var self = this;
            this.renderElement();
            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });
            console.log("queso: " + invoice);

            this.render_list(invoice);

            this.$('.invoice-list-contents').delegate('.invoice-line', 'click', function(event) {
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });

            var search_timeout = null;

            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            /*             this.$('.searchbox input').on('keyup', function(event) {
                            clearTimeout(search_timeout);
                            var query = this.value;
                            search_timeout = setTimeout(function() {
                                self.perform_search(query, event.which === 13);
                            }, 70);
                        });

                        this.$('.searchbox .search-clear').click(function() {
                            self.clear_search();
                        }); */
        },

        render_list: function(invoices) {
            var contents = this.$el[0].querySelector('.invoice-list-contents');
            contents.innerHTML = "";
            for (var i = 0, len = Math.min(invoices.length, 1000); i < len; i++) {
                var invoice = invoices[i];
                var invoice_line_html = QWeb.render('PosInvoiceLine', { widget: this, invoice: invoice });
                var invoice_line = document.createElement('tbody');
                invoice_line.innerHTML = invoice_line_html;
                invoice_line = invoice_line.childNodes[1];
                contents.appendChild(invoice_line);
            }
        },

        /*         perform_search: function(query, associate_result) {
                    var orders;
                    if (query) {
                        orders = this.search_order(query);
                        this.render_list(orders);
                    } else {
                        orders = this.pos.orders;
                        this.render_list(orders);
                    }
                },
                clear_search: function() {
                    var orders = this.pos.orders;
                    this.render_list(orders);
                    this.$('.searchbox input')[0].value = '';
                    this.$('.searchbox input').focus();
                },

                search_order: function(query) {
                    try {
                        var re = RegExp(query, 'i');
                    } catch (e) {
                        return [];
                    }
                    var results = [];
                    for (var order_id in this.pos.orders) {
                        var r = re.exec(this.pos.orders[order_id]['name'] + '|' + this.pos.orders[order_id]['partner_id'][1]);
                        if (r) {
                            results.push(this.pos.orders[order_id]);
                        }
                    }
                    return results;
                }, */

        line_select: function(event, $line, id) {
            var self = this;

            var fnc_select_element = function(invoice) {
                this.$('.invoice-list .lowlight').removeClass('lowlight')

                if ($line.hasClass('highlight')) {
                    $line.removeClass('highlight');
                    $line.addClass('lowlight');
                    this.display_invoice_details('hide', invoice)
                } else {
                    this.$('.invoice-list .highlight').removeClass('highlight')
                    $line.addClass('highlight');
                    var y = event.pageY - $line.parent().offset().top;
                    this.display_invoice_details('show', invoice, y);
                    this.invoice = invoice;
                }
            }.bind(this)
            this._rpc({
                model: "account.move",
                method: "search_read",
                args: [
                    [
                        ["id", "=", id]
                    ],
                    [
                        "name",
                        "amount_total",
                        "partner_id"
                    ]
                ],
            }).then(fnc_select_element);
            /*             var order = this.get_order_by_id(id);
                        $line.addClass('highlight');
                        this.gui.show_popup('order', {
                            'order': order,
                            'line': $line
                        }) */
        },
        display_invoice_details: function(visibilty, invoice, clickpos) {
            var self = this;

            var contents = this.$('.invoice-details-contents');
            var parent = this.$('invoice-list').parent();
            var scroll = parent.scrollTop();
            var height = contents.height();
            var $button_next = this.$(".button.next");

            invoice = invoice[0];

            if (visibilty === "show") {
                contents.empty();
                $button_next.removeClass("oe_hidden");

                $button_next.off("click");
                $button_next.on("click", function(event) { self.invoice_register_popup(invoice); });

                contents.append($(QWeb.render('InvoiceDetails', { widget: this, move: invoice })))

                var new_height = contents.height();

                if (!this.details_visible) {
                    parent.height("-=" + new_height);

                    if (clickpos < scroll + new_height + 20) {
                        parent.scrollTop(clickpos - 20);
                    } else {
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                } else {
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
            } else if (visibilty === "hide") {
                contents.empty();
                $button_next.addClass("oe_hidden");
                parent.height("100%");
                if (height > scroll) {
                    contents.css({ height: height + 'px' });
                    contents.animate({ height: 0 }, 400, function() {
                        contents.css({ height: '' });
                    });
                } else {
                    parent.scrollTop(parent.scrollTop() - height);
                }
                this.details_visible = false;
            }
        },

        invoice_register_popup: function(invoice) {
            self = this;
            var show_register_popup = function(values) {
                var options = {
                    "invoice": invoice,
                    "journal_ids": values[0],
                    "payment_method_ids": values[1]
                }
                self.gui.show_popup("invoice_payment", options);
            }

            var payment_methods = this._rpc({
                model: "account.payment.method",
                method: "search_read",
                args: [
                    [],
                    ["name"]
                ],
            });

            var journals = this._rpc({
                model: "account.journal",
                method: "search_read",
                args: [
                    [
                        ["type", "in", ["bank", "cash"]]
                    ],
                    ["display_name"]
                ],
            });

            Promise.all([journals, payment_methods]).then(show_register_popup);

        }
    });

    gui.define_screen({ name: 'invoice_list', widget: PosInvoiceScreenWidget });


    var InvoicePaymentPopupWidget = PopupWidget.extend({
        template: 'InvoicePaymentPopupWidget',
        show: function(options) {
            var self = this;
            options = options || {};

            this._super(options);
            this.invoice = options.invoice || {};
            this.payment_methods = options.payment_methods || [];
            this.renderElement();
        },
        click_confirm: function(event) {
            alert("Invoice name: " + this.invoice.name);

            var today = new Date();

            var year = today.getFullYear();
            var month = ("0" + today.getMonth()).slice(-2);
            var day = ("0" + today.getDate()).slice(-2);

            var str_today = year + "-" + month + "-" + day;

            var journals = this._rpc({
                model: "account.payment",
                method: "create",
                args: [
                    [{
                        "payment_type": "inbound",
                        "journal_id": parseInt(this.$('#journal_id').val()),
                        "partner_type": "customer",
                        "amount": parseFloat(this.$('#amount').val()),
                        "payment_method_id": parseInt(this.$('#payment_method_id').val()),
                        "payment_date": str_today,
                        "partner_id": parseInt(this.invoice.partner_id[0]),
                        "invoice_ids": [
                            [4, this.invoice.id, 0]
                        ],
                        "communication": this.invoice.name
                    }]
                ],
            }).then(function(result) {
                alert("resultado:" + result);
            });
            this.gui.close_popup();
        }
    });
    gui.define_popup({ name: 'invoice_payment', widget: InvoicePaymentPopupWidget });
});