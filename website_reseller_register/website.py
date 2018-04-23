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
import base64
import sys
import traceback

import logging
_logger = logging.getLogger(__name__)


PARTNER_FIELDS = ['name', 'street', 'street2', 'zip', 'city', 'country_id', 'phone', 'email']

class reseller_register(http.Controller):

    # can be overrided with more company field
    def get_company_post(self, post):
        value = {'name': post.get('company_name'), 'company_registry': post.get('company_registry')}
        return value

    # can be overrided with more company field
    def company_fields(self):
        return ['name']

    # can be overrided with more company field
    def contact_fields(self):
        return ['name','phone','mobile','email','image','attachment']

    # can be overrided with more address type
    def get_address_type(self):
        return ['delivery', 'invoice', 'contact']

    # can be overrided with more address type
    def get_children_post(self, issue, post):
        address_type = self.get_address_type()
        children = {}
        validations = {}
        for at in address_type:
            child = self.get_child(issue, at, post)
            children[at] = child['child']
            validations.update(child['validation'])
        return {'children': children, 'validations': validations}

    # can be overrided with more address type
    def get_children(self, issue):
        address_type = self.get_address_type()
        children = {}
        for at in address_type:
            children[at] = issue.partner_id.child_ids.filtered(lambda c: c.type == at)
        return children

    def get_child(self, issue, address_type, post):
        validation = {}
        child_dict = {}
        for k,v in post.items():
            if k.split('_')[0] == address_type:
                if len(k.split('_')) > 2:
                    child_dict['_'.join(k.split('_')[1:])] = v
                else:
                    child_dict[k[1]] = v
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
        return {'child': None, 'validation': validation}

    # can be overrided with more help text
    def get_help(self):
        help = {}
        help['help_company_name'] = _('')
        help['help_company_registry'] = _('')
        help['help_delivery_street'] = _('')
        help['help_delivery_street2'] = _('')
        help['help_delivery_zip'] = _('')
        help['help_delivery_city'] = _('')
        help['help_delivery_country_id'] = _('')
        help['help_delivery_phone'] = _('')
        help['help_delivery_email'] = _('')
        help['help_invoice_street'] = _('')
        help['help_invoice_street2'] = _('')
        help['help_invoice_zip'] = _('')
        help['help_invoice_city'] = _('')
        help['help_invoice_country_id'] = _('')
        help['help_invoice_phone'] = _('')
        help['help_invoice_email'] = _('')
        help['help_contact_street'] = _('')
        help['help_contact_street2'] = _('')
        help['help_contact_zip'] = _('')
        help['help_contact_city'] = _('')
        help['help_contact_image'] = _('Please a picture of you. This makes it more personal.')
        help['help_contact_mobile'] = _('Contatcs Cell')
        help['help_contact_phone'] = _('Contatcs phone')
        help['help_contact_email'] = _('Please add an email address')
        help['help_contact_attachment'] = _('If you have more information or a diploma, you can attach it here. You can add more than one, but you have to save each one separate.')
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
                'active': False,
                'property_invoice_type': None,
                'website_short_description': None,
            })
            issue = request.env['project.issue'].sudo().create({
                'name': 'New Reseller Application',
                'partner_id': partner.id,
                'project_id': request.env.ref('website_reseller_register.project_reseller_register').id
            })
            return partner.redirect_token('/reseller_register/%s' %issue.id)
        elif request.httprequest.method == 'POST':
            self.update_partner_info(issue, post)
            issue = request.env['project.issue'].sudo().browse(int(issue))
        else:
            issue = request.env['project.issue'].sudo().browse(int(issue))
            if not issue.partner_id.check_token(post.get('token')):
                return request.website.render('website.403', {})
            children = self.get_children(issue)
        help = self.get_help()
        value = {
            'issue': issue,
            'help': help,
            'validation': validation,
            'country_selection': [(country['id'], country['name']) for country in request.env['res.country'].search_read([], ['name'])],
            'invoice_type_selection': [(invoice_type['id'], invoice_type['name']) for invoice_type in request.env['sale_journal.invoice.type'].sudo().search_read([], ['name'])],
        }
        if any(children):
            for k,v in children.items():
                value[k] = v
        return request.website.render('website_reseller_register.register_form', value)

    # can be overrided
    def update_partner_info(self, issue, post):
        issue = request.env['project.issue'].sudo().browse(int(issue))
        if not issue.partner_id.check_token(post.get('token')):
            return request.website.render('website.403', {})
        if post.get('invoicetype'):
            issue.partner_id.write({'property_invoice_type': int(post.get('invoicetype'))})
        issue.partner_id.write({'website_short_description': post.get('website_short_description', '')})
        issue.partner_id.write(self.get_company_post(post))
        children_dict = self.get_children_post(issue, post)
        children = children_dict['children']
        validation = children_dict['validations']
        for field in self.company_fields():
            validation['company_%s' %field] = 'has-success'

    @http.route(['/reseller_register/<int:issue>/contact/new', '/reseller_register/<int:issue>/contact/<int:contact>'], type='http', auth='public', website=True)
    def reseller_contact_new(self, issue=0, contact=0, **post):
        issue = request.env['project.issue'].sudo().browse(issue)
        if not issue.partner_id.check_token(post.get('token')):
            return request.website.render('website.403', {})
        if contact > 0:
            contact = request.env['res.partner'].sudo().browse(contact)
            if not (contact in issue.partner_id.child_ids):
                contact = request.env['res.partner'].sudo().browse([])
        else:
            contact = request.env['res.partner'].sudo().browse([])

        validation = {}
        if request.httprequest.method == 'POST':
            # Values
            values = {f: post['contact_%s' % f] for f in self.contact_fields() if post.get('contact_%s' % f) and f not in ['attachment','image']}
            if post.get('image'):
                image = post['image'].read()
                values['image'] = base64.encodestring(image)
            if post.get('attachment'):
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': post['attachment'].filename,
                    'res_model': 'res.partner',
                    'res_id': contact.id,
                    'datas': base64.encodestring(post['attachment'].read()),
                    'datas_fname': post['attachment'].filename,
                })
            values['parent_id'] = issue.partner_id.id
            # Validation and store
            for field in self.contact_fields():
                validation['contact_%s' %field] = 'has-success'
            if not values.get('contact_name'):
                validation['contact_name'] = 'has-error'
            if not 'has-error' in validation:
                if not contact:
                    if values.get('email') in request.env['res.users'].sudo().search([]).mapped('login'):
                        validation['contact_email'] = 'has-error'
                        contact = request.env['res.partner'].sudo().browse([])
                        help_dic = self.get_help()
                        help_dic['help_contact_email'] = _('This email is alreay exist. Choose another one!')
                        return request.website.render('website_reseller_register.contact_form', {
                            'issue': issue,
                            'contact': contact,
                            'help': help_dic,
                            'validation': validation,
                        })
                    try:
                        user = request.env['res.users'].sudo().with_context(no_reset_password=True).create({
                            'name': values.get('name'),
                            'login': values.get('email'),
                            'image': values.get('image'),
                        })
                        user.partner_id.sudo().write({
                            'email': values.get('email'),
                            'phone': values.get('phone'),
                            'mobile': values.get('mobile'),
                            'parent_id': values.get('parent_id'),
                        })
                        try:
                            user.action_reset_password()
                        except:
                            _logger.warn('Cannot send mail to %s. Please check your mail server configuration.' %user.name)
                    except Exception as e:
                        err = sys.exc_info()
                        error = ''.join(traceback.format_exception(err[0], err[1], err[2]))
                        _logger.info('Cannot create user %s: %s' % (values.get('name'), error))
                else:
                    contact.sudo().write(values)
                return request.redirect('/reseller_register/%s?token=%s' %(issue.id, post.get('token')))
        else:
            issue = request.env['project.issue'].sudo().browse(int(issue))
        return request.website.render('website_reseller_register.contact_form', {
            'issue': issue,
            'contact': contact,
            'help': self.get_help(),
            'validation': validation,
        })

    @http.route(['/reseller_register/<int:issue>/contact/<int:contact>/delete'], type='http', auth='public', website=True)
    def reseller_contact_delete(self, issue=0, contact=0, **post):
        issue = request.env['project.issue'].sudo().browse(issue)
        if contact > 0:
            contact = request.env['res.partner'].sudo().browse(contact)
            if not (contact in issue.partner_id.child_ids):
                contact = request.env['res.partner'].sudo().browse([])
        else:
            contact = request.env['res.partner'].sudo().browse([])
        if contact:
            request.env['res.users'].search([('partner_id', '=', contact.id)]).unlink()
        contact.unlink()
        validation = {}
        for k in self.contact_fields():
            validation[k] = 'has-success'
        return request.redirect('/reseller_register/%s?token=%s' %(issue.id, issue.partner_id.token))

    @http.route(['/reseller_register/<int:issue>/attachment/<int:attachment>/delete'], type='http', auth='public', website=True)
    def reseller_attachment_delete(self, issue=0, attachment=0, **post):
        issue = request.env['project.issue'].sudo().browse(issue)
        if attachment > 0:
            attachment = request.env['ir.attachment'].sudo().browse(attachment)
            if attachment.res_model == 'res.partner' and attachment.res_id != 0:
                contact = request.env['res.partner'].browse(attachment.res_id)
                if contact.parent_id == issue.partner_id:
                    attachment.unlink()
                    return request.redirect('/reseller_register/%s/contact/%s?token=%s' %(issue.id, contact.id, issue.partner_id.token))
        return request.redirect('/reseller_register/%s?token=%s' %(issue.id, issue.partner_id.token))

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
