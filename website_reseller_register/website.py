# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.addons.web import http
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)


PARTNER_FIELDS = ['name', 'street', 'street2', 'zip', 'city', 'phone', 'email']

class reseller_register(http.Controller):

    # can be overrided with more company field
    def get_company_post(self, post):
        value = {'name': post.get('company_name')}
        return value

    # can be overrided with more company field
    def company_fileds(self):
        return ['name']

    # can be overrided with more address type
    def get_children_post(self, issue, post):
        address_type = ['delivery', 'invoice', 'contact']
        children = {}
        validations = {}
        for at in address_type:
            child = self.get_child(issue, at, post)
            children[at] = child['child']
            validations.update(child['validation'])
        return {'children': children, 'validations': validations}

    # can be overrided with more address type
    def get_children(self, issue):
        address_type = ['delivery', 'invoice', 'contact']
        children = {}
        for at in address_type:
            children[at] = issue.partner_id.child_ids.filtered(lambda c: c.type == at)
        return children

    def get_child(self, issue, address_type, post):
        validation = {}
        child_dict = {k.split('_')[1]:v for k,v in post.items() if k.split('_')[0] == address_type}
        if any(child_dict):
            if address_type != 'contact':
                child_dict['name'] = address_type
            child_dict['parent_id'] = issue.partner_id.id
            child_dict['type'] = address_type
            child_dict['use_parent_address'] = False
            child = issue.partner_id.child_ids.filtered(lambda c: c.type == address_type)
            if not child:
                child = request.env['res.partner'].sudo().create(child_dict)
            else:
                child.write(child_dict)
            for field in PARTNER_FIELDS:
                validation['%s_%s' %(address_type, field)] = 'has-success'
        return {'child': child, 'validation': validation}

    # can be overrided with more help text
    def get_help(self):
        help = {}
        help['help_company_name'] = _('')
        help['help_delivery_street'] = _('')
        help['help_delivery_street2'] = _('')
        help['help_delivery_zip'] = _('')
        help['help_delivery_city'] = _('')
        help['help_delivery_phone'] = _('')
        help['help_delivery_email'] = _('')
        help['help_invoice_street'] = _('')
        help['help_invoice_street2'] = _('')
        help['help_invoice_zip'] = _('')
        help['help_invoice_city'] = _('')
        help['help_invoice_phone'] = _('')
        help['help_invoice_email'] = _('')
        help['help_contact_street'] = _('')
        help['help_contact_street2'] = _('')
        help['help_contact_zip'] = _('')
        help['help_contact_city'] = _('')
        help['help_contact_phone'] = _('')
        help['help_contact_email'] = _('')
        return help

    @http.route(['/reseller_register/new', '/reseller_register/<int:issue>'], type='http', auth='public', website=True)
    def reseller_register_new(self, issue=0, **post):
        validation = {}
        children = {}
        help = {}
        if not issue:
            partner = request.env['res.partner'].sudo().create({
                'name': _('My Company'),
                'is_company': True,
                'active': False
            })
            issue = request.env['project.issue'].sudo().create({
                'name': 'New Reseller Application',
                'partner_id': partner.id,
                'project_id': request.env.ref('website_reseller_register.project_reseller_register').id
            })
        elif request.httprequest.method == 'POST':
            issue = request.env['project.issue'].sudo().browse(int(issue))
            issue.partner_id.write(self.get_company_post(post))
            children_dict = self.get_children_post(issue, post)
            children = children_dict['children']
            validation = children_dict['validations']
            for field in self.company_fileds():
                validation['company_%s' %field] = 'has-success'
        else:
            issue = request.env['project.issue'].sudo().browse(int(issue))
            children = self.get_children(issue)
        help = self.get_help()
        value = {
            'issue': issue,
            'help': help,
            'validation': validation,
        }
        if any(children):
            for k,v in children.items():
                value[k] = v
        return request.website.render('website_reseller_register.register_form', value)

    @http.route(['/website_reseller_register_message_send'], type='json', auth="public", website=True)
    def website_reseller_register_message_send(self, issue_id, msg_body, **kw):
        if msg_body != '':
            message = request.env['mail.message'].sudo().create({
                'model': 'project.issue',
                'res_id': int(issue_id),
                'type': 'comment',
                'body': msg_body,
                'author_id': request.env.user.partner_id.id
            })
            if message:
                return True
        return False
