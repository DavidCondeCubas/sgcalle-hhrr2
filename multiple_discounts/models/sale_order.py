# -*- coding: utf-8 -*-

from odoo import models, fields, _


def get_parent_category(category_id):
    single_list = [category_id]
    if category_id.parent_id:
        single_list.extend(get_parent_category(category_id.parent_id))
        return single_list
    else:
        return single_list


def apply_discount(move_id, discount_ids):
    write_lines = []
    for invoice_line in move_id.invoice_line_ids:
        invoice_line_categories = get_parent_category(
            invoice_line.product_id.categ_id)
        discount_applicable = discount_ids.filtered(
            lambda discount: discount.category_id in invoice_line_categories)

        for discount in discount_applicable:
            percent = discount.percent
            discount_count = -invoice_line.price_total * (percent/100)

            write_lines.append(
                (0, 0, {
                    "product_id": discount.product_id.get_single_product_variant().get("product_id", False),
                    "price_unit": discount_count,
                    "analytic_account_id": discount.analytic_account_id.id,
                    }
                )
            )

    move_id.write({
        "invoice_line_ids": write_lines
    })



class SaleOrder(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        moves = super(SaleOrder, self).create_invoices()
        if moves.get("name", "") == "Invoices":
            res_ids = []

            # If res is 0 there are more than one invoice, so
            # we have to find the ids in the domain
            if moves["res_id"] != 0:
                res_ids.append(moves["res_id"])
            else:
                id_domain = list(
                    filter(lambda condition: condition[0] == "id", moves.get("domain", [])))[0]
                if id_domain:
                    ids = id_domain[2]
                    res_ids = ids

            move_ids = self.env["account.move"].browse(res_ids)
            sale_ids = self.env["sale.order"].browse(
                self._context.get("active_ids", []))

            # Apply discount to every move
            for move in move_ids:
                sale_order = sale_ids.filtered(
                    lambda order: move in order.invoice_ids)
                discount_ids = sale_order.partner_id.discount_ids

                move.mapped(lambda move: apply_discount(move, discount_ids))
        return moves
