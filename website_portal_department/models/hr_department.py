from odoo import fields, models, api
from odoo.tools.translate import html_translate
from lxml import etree
from markupsafe import Markup


class Department(models.Model):
    _inherit = 'hr.department'

    department_header = fields.Html('Department Header', sanitize_attributes=False,
                                    translate=html_translate, default="<p></p>")

    # @api.model
    # def render_from_field(self, template, website_description=None, value=None):
    #     view_id = self.env['ir.ui.view']._get_view_id(template)
    #     template = self.env['ir.ui.view'].sudo()._read_template(view_id)
    #     if website_description:
    #         template = template.replace('</div>', website_description + '</div>')
    #         template = template.replace('<br>', '<br/>')
    #     view = etree.fromstring(Markup(template))
    #     if value:
    #         value_dict = {'sale_order': value}
    #         res = self.env['ir.qweb']._render(view, value_dict)
    #     else:
    #         try:
    #             res = self.env['ir.qweb']._render(view)
    #         except:
    #             return
    #     return res
