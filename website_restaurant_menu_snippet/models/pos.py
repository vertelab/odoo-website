from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class POSCategory(models.Model):
    _inherit = "pos.category"

    def _get_default_website_id(self):
        _logger.info("_get_default_website_id körs")
        Website = self.env['website']
        websites = Website.search([])
        return len(websites) == 1 and websites or Website

    website_id = fields.Many2one('website', default=_get_default_website_id)

    @api.depends('name')
    def _set_products(self):
        _logger.info("_set_products körs")
        for rec in self:
            rec.product_tmpl_ids = self.env['product.product'].search([('pos_categ_ids', 'in', rec.id)])

    product_tmpl_ids = fields.Many2many('product.product', string="Products",
                                        compute=_set_products, store=False)
