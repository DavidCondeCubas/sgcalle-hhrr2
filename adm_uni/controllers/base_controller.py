from odoo import http
import json

class BaseController(http.Controller):
    @http.route("/admission/languages", auth="public", methods=["GET"])
    def get_languages(self, **params):
        # print(http.request.httprequest.args.getlist("test"))
        LanguagesEnv = http.request.env['adm_uni.languages']
        
        language_ids = LanguagesEnv.browse(LanguagesEnv.search([]))
        
        return json.dumps(language_ids.ids)
