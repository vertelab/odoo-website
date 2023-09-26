from odoo import models, api, fields


class POSCategory(models.Model):
    _inherit = "pos.category"

    def _get_default_website_id(self):
        Website = self.env['website']
        websites = Website.search([])
        return len(websites) == 1 and websites or Website

    website_id = fields.Many2one('website', default=_get_default_website_id)
    product_tmpl_ids = fields.One2many('product.template', 'pos_categ_id', string="Products")


