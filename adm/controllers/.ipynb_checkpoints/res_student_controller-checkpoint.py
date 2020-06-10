from odoo import http
import json

class BaseController(http.Controller):
    
    @http.route("/admission/student", auth="none", methods=["GET"], cors="*")
    def get_languages(self, **params):
        PartnerEnv = http.request.env['res.partner']
        partner_ids = PartnerEnv.sudo().search([("id", ">", 50)])
        
        partners = partner_ids.read(["name", "function"])
        
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(partners)
        response = http.Response(body, headers=headers)
        
        # Response Status Code
        response.status_code = 200
        
        return response
        
