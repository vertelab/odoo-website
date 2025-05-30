from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'sequence'

    available_in_menu = fields.Boolean(
        string="Available in website menu",
        help="If the product is displayed in the website menu or not",
        default=True,
    )
    
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of product categories.",
        default=1,
    )
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'sequence'
    
    available_in_menu = fields.Boolean(
        string="Available in website menu",
        help="If the product is displayed in the website menu or not",
        default=True,
    )
    
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of product categories.",
        default=1,
    )

class ProductCombo(models.Model):
    _inherit = 'product.combo'
    _order = 'sequence'
    
    available_in_menu = fields.Boolean(
        string="Available in website menu",
        help="If the combo is displayed in the website menu or not",
        default=True,
    )
    
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of product categories.",
        default=1,
    )
