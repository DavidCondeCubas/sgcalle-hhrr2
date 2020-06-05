# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalApplication(CustomerPortal):
     
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = http.request.env.user.partner_id
        values['has_application'] = http.request.env["adm_uni.application"].search([ ("partner_id", "=", partner.id) ])
        return values

    #@property
    #def MANDATORY_BILLING_FIELDS(self):
    #    return super().MANDATORY_BILLING_FIELDS + ["first_name", "last_name", "middle_name"]

    @property
    def OPTIONAL_BILLING_FIELDS(self):
        return super().OPTIONAL_BILLING_FIELDS + ["first_name", "last_name", "middle_name"]

