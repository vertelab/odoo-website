from odoo import fields, models, api
from odoo.tools.translate import html_translate
from odoo.addons.http_routing.models.ir_http import slug
from lxml import etree
from markupsafe import Markup


class Department(models.Model):
    _inherit = [
        "hr.department",
        'website.published.multi.mixin',
    ]
    _name = 'hr.department'

    department_header = fields.Html('Department Header', sanitize_attributes=False,
                                    translate=html_translate, default="<p></p>")

    @api.depends('name')
    def _compute_website_url(self):
        super(Department, self)._compute_website_url()
        for dept in self:
            if dept.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                dept.website_url = '/dept_builder/%s' % slug(dept)

