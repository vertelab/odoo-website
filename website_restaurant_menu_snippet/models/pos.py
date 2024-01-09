from odoo import models, api, fields


class POSCategory(models.Model):
    _inherit = "pos.category"

    def _get_default_website_id(self):
        Website = self.env['website']
        websites = Website.search([])
        return len(websites) == 1 and websites or Website

    website_id = fields.Many2one('website', default=_get_default_website_id)

    @api.depends('name')
    def _set_products(self):
        for rec in self:
            rec.product_tmpl_ids = self.env['product.template'].search([('pos_categ_ids', 'in', rec.id)])

    product_tmpl_ids = fields.Many2many('product.template', string="Products",
                                        compute=_set_products, store=True)

    # @api.depends('product_tmpl_ids')
    # def _set_has_published_products(self):
    #     for rec in self:
    #         if rec.product_tmpl_ids and rec.product_tmpl_ids.filtered(lambda prod: prod.website_published):
    #             rec.has_published_products = True
    #         else:
    #             rec.has_published_products = False
    #
    # has_published_products = fields.Boolean(compute=_set_has_published_products)
