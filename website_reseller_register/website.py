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

    @http.route(['/reseller_register/new', '/reseller_register/<model("project.issue"):issue>'], type='http', auth='public', website=True)
    def reseller_register_new(self, issue=None, **post):
        validation = {}
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
            partner = issue.partner_id
            partner.name = post.get('company_name')
            delivery_dict = {k.split('_')[1]:v for k,v in post.items() if k.split('_')[0] == 'delivery'}
            if any(delivery_dict):
                delivery_dict['name'] = _('Delivery')
                delivery_dict['parent_id'] = issue.partner_id.id
                delivery_dict['type'] = 'delivery'
                delivery_dict['use_parent_address'] = False
                delivery = issue.partner_id.child_ids.filtered(lambda c: c.type == 'delivery')
                if not delivery:
                    delivery = request.env['res.partner'].sudo().create(delivery_dict)
                else:
                    delivery.write(delivery_dict)
                for field in PARTNER_FIELDS:
                    validation['delivery_%s' %field] = 'has-success'
            invoice_dict = {k.split('_')[1]:v for k,v in post.items() if k.split('_')[0] == 'invoice'}
            if any(invoice_dict):
                invoice_dict['name'] = _('Invoice')
                invoice_dict['parent_id'] = issue.partner_id.id
                invoice_dict['type'] = 'invoice'
                invoice_dict['use_parent_address'] = False
                invoice = issue.partner_id.child_ids.filtered(lambda c: c.type == 'invoice')
                if not delivery:
                    invoice = request.env['res.partner'].sudo().create(invoice_dict)
                else:
                    invoice.write(invoice_dict)
                for field in PARTNER_FIELDS:
                    validation['invoice_%s' %field] = 'has-success'
            contact_dict = {k.split('_')[1]:v for k,v in post.items() if k.split('_')[0] == 'contact'}
            if any(contact_dict):
                contact_dict['parent_id'] = issue.partner_id.id
                contact_dict['type'] = 'contact'
                contact_dict['use_parent_address'] = False
                contact = issue.partner_id.child_ids.filtered(lambda c: c.type == 'contact')
                if not delivery:
                    contact = request.env['res.partner'].sudo().create(contact_dict)
                else:
                    contact.write(contact_dict)
                for field in PARTNER_FIELDS:
                    validation['contact_%s' %field] = 'has-success'
            _logger.warn('%s\n%s\n%s' %(delivery_dict, invoice_dict, contact_dict))
        else:
            delivery = issue.partner_id.child_ids.filtered(lambda c: c.type == 'delivery')
            invoice = issue.partner_id.child_ids.filtered(lambda c: c.type == 'invoice')
            contact = issue.partner_id.child_ids.filtered(lambda c: c.type == 'contact')
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
        return request.website.render('website_reseller_register.new', {
            'issue': issue,
            'delivery': delivery,
            'invoice': invoice,
            'contact': contact,
            'help': help,
            'validation': validation
        })

