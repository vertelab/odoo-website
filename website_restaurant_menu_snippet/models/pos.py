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
    
    available_in_menu = fields.Boolean(
        string="Available in website menu",
        help="If the combo is displayed in the website menu or not",
        default=True,
    )

    @api.depends('name')
    def _set_products(self):
        _logger.info("_set_products körs")
        for rec in self:
            rec.product_tmpl_ids = self.env['product.template'].search([('pos_categ_ids', 'in', rec.id), ('available_in_menu', '=', True)])

    product_tmpl_ids = fields.Many2many('product.template', string="Products",
                                        compute=_set_products, store=True)

