from odoo import api, fields, models, _
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    def get_pricelist(self):
        pricelist = self.env.user.commercial_partner_id.property_product_pricelist
        return pricelist

    def get_attribs(self):
        attrib_list = request.httprequest.args.getlist("attrib")
        return attrib_list
