# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import Controller, request, route
from odoo.addons.http_routing.models.ir_http import unslug


class QuotationBuilderController(Controller):

    @route(["/dept_builder/<string:dept_id>"], type='http', auth='user', website=True)
    def dept_builder_template_view(self, dept_id, **post):
        template_id = unslug(dept_id)[-1]
        hr_department = request.env['hr.department'].browse(template_id).with_context(
            allowed_company_ids=request.env.user.company_ids.ids,
        )
        return request.render('website_portal_department.dept_template', {'hr_department': hr_department})
