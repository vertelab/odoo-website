# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
# from odoo.addons.sale.controllers.portal import CustomerPortal, portal_pager, get_records_pager
from odoo.http import content_disposition, Controller, request, route

from odoo.osv import expression


class CustomerPortalXtend(CustomerPortal):

    @route(['/activities/counters'], type='json', auth="user", website=True)
    def activities_counters(self, counters, **kw):
        values = {}
        if 'quotation_activities_count' in counters:
            quotation = request.env['sale.order'].search([
                ('state', 'in', ['sent', 'cancel']), ('show_on_customer_portal', '=', True)
            ]) if request.env['sale.order'].check_access_rights('read', raise_exception=False) else False
            if quotation:
                quotation_activities = quotation.sudo().mapped('activity_ids')
                values['quotation_activities_count'] = len(quotation_activities)
            else:
                values['quotation_activities_count'] = 0
        if 'sale_activities_count' in counters:
            sale_order = request.env['sale.order'].search([
                ('state', 'in', ['sale', 'done']), ('show_on_customer_portal', '=', True)
            ]) if request.env['sale.order'].check_access_rights('read', raise_exception=False) else False
            if sale_order:
                sale_order_activities = sale_order.sudo().mapped('activity_ids')
                values['sale_activities_count'] = len(sale_order_activities)
            else:
                values['sale_activities_count'] = 0

        if 'project_activities_count' in counters:
            project_project_activities = request.env['mail.activity'].search([('res_model', '=', 'project.project')]) \
                if request.env['mail.activity'].check_access_rights('read', raise_exception=False) else 0

            if project_project_activities:
                project_project = request.env['project.project'].sudo().browse(project_project_activities.mapped('res_id')). \
                    filtered(lambda project: project.show_on_customer_portal)

                values['project_activities_count'] = len(project_project)
            else:
                values['project_activities_count'] = 0

        if 'task_activities_count' in counters:
            project_task = request.env['project.task'].search([('show_on_customer_portal', '=', True)]) \
                if request.env['project.task'].check_access_rights('read', raise_exception=False) else False
            if project_task:
                project_task_activities = project_task.sudo().mapped('activity_ids')
                values['task_activities_count'] = len(project_task_activities)
            else:
                values['task_activities_count'] = 0
        return values

