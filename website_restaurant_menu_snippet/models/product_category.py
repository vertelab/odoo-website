from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'
    _order = 'sequence'

    available_in_menu = fields.Boolean(
        string="Available in website menu",
        help="If the Point of Sale category is displayed in the website menu or not",
        default=True,
    )

    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of product categories.",
        default=1,
    )
