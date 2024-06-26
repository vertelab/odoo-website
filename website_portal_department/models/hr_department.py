from odoo import fields, models, api
from odoo.tools.translate import html_translate
from lxml import etree
from markupsafe import Markup


class Department(models.Model):
    _inherit = 'hr.department'

    department_header = fields.Html('Department Header', sanitize_attributes=False,
                                    translate=html_translate, default="<p></p>")

