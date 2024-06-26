from odoo import fields, models, api
from odoo.tools.translate import html_translate


class Users(models.Model):
    _inherit = 'res.users'

    @api.depends('employee_id')
    def _compute_department_header(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.department_id:
                rec.department_header = rec.employee_id.department_id.department_header
            else:
                rec.department_header = "<p></p>"

    def _inverse_department_header(self):
        self.employee_id.department_id.department_header = self.department_header

    department_header = fields.Html('Department Header', sanitize_attributes=False,
                                    translate=html_translate, compute=_compute_department_header,
                                    inverse=_inverse_department_header)
