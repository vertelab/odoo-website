# -*- coding: utf-8 -*-
##############################################################################
##
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
from openerp.exceptions import ValidationError
import base64
import sys
import traceback
import re
import openerp
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.web.controllers.main import ensure_db
 
import logging
_logger = logging.getLogger(__name__)

#TODO:
#1. Connect reseller with "agents" field in the partner form. I can see that with flow but it can not saved :(
#2. create an user when create a partner, it is not done yet, I tried some function from core _create_user() But it is missing sth, So it it not 
#   working. If we can create a user when create a partner, we can set up en maller for sending emails which is easier (Maybe?)

PARTNER_FIELDS = ['name','agents', 'customer_no','street', 'street2', 'zip', 'city', 'country_id', 'phone', 'email']

class consumer_register(http.Controller):
    _name="consumer.register"
    #Do I need this ?
    # ~ reseller_id = fields.Many2many(
        # ~ comodel_name="res.partner", relation="partner_agent_rel",
        # ~ column1="partner_id", column2="agent_id",
        # ~ domain="[('agent', '=', True)]")
        
    # can be overriden with more consumer fields
    def get_consumer_post(self, post):
        return {'name': post.get('consumer_name'),
        # ~ 'customer_no': contact.id,
        # ~ 'agents':post.get('reseller_id'),
        'agents':'Skogsro Spa',
        'street':post.get('delivery_street'),
        'street2':post.get('delivery_street2'),
        'zip':post.get('delivery_zip'),
        'city':post.get('delivery_city'),
        'phone':post.get('delivery_phone'),
        'email':post.get('delivery_email'),
        'login':post.get('delivery_email'),
        }
        

    # can be overriden with more consumer fields
    def consumer_fields(self):
        return ['name','agents']

    # can be overriden with more consumer fields
    def contact_fields(self):
        return ['name','phone','mobile','email','image','attachment']

    # can be overriden with more address types
    def get_address_type(self):
        return ['delivery', 'invoice', 'contact']

    # can be overriden with more address types
    def get_children_post(self, issue, post):
        address_type = self.get_address_type()
        children = {}
        validations = {}
        for at in address_type:
            child = self.get_child(issue, at, post)
            children[at] = child['child']
            validations.update(child['validation'])
        return {'children': children, 'validations': validations}

    # can be overriden with more address types
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
                    if '_'.join(k.split('_')[1:]) == 'country_id':
                        child_dict['_'.join(k.split('_')[1:])] = int(v)
                    else:
                        child_dict['_'.join(k.split('_')[1:])] = v
                else:
                    child_dict[k.split('_')[1]] = v
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
                child.sudo().write(child_dict)
            for field in PARTNER_FIELDS:
                validation['%s_%s' %(address_type, field)] = 'has-success'
            return {'child': child, 'validation': validation}
        return {'child': None, 'validation': validation}

    # can be overrided with more help text
    def get_help(self):
        help = {}
        help['help_consumer_name'] = _('')
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
        help['help_contact_image'] = _('Please add a picture of yourself. This makes it more personal.')
        help['help_contact_mobile'] = _('Contatcs Cell')
        help['help_contact_phone'] = _('Contatcs phone')
        help['help_category_id'] = _('Labels')
        help['help_contact_email'] = _('Please add an email address')
        help['help_contact_attachment'] = _('If you have more information or a diploma, you can attach it here. You can add more than one, but you have to save each one separate.')
        return help

    def set_issue_id(self, issue_id):
        request.session['consumer_register_issue_id'] = issue_id

    def get_issue(self, issue_id, token):
        """Fetch the specified issue, or the issue from the session. Check token if needed.
        """
        issue_id = (issue_id and int(issue_id)) or request.session.get('consumer_register_issue_id')
        if not issue_id:
            return
        issue = request.env['project.issue'].sudo().search([('id', '=', issue_id)])
        if not issue:
            # Issue has probably been deleted
            self.set_issue_id(None)
            return
        if issue_id == request.session.get('consumer_register_issue_id'):
            return issue
        elif issue.partner_id.check_token(token):
            self.set_issue_id(issue.id)
            return issue
        return
    
    @http.route(['/consumer_register/new', '/consumer_register/<int:issue_id>', '/consumer_register/<int:issue_id>/<string:action>'], type='http', auth='public', website=True)
    def consumer_register_new(self, issue_id=None, action=None, **post):
        validation = {}
        children = {}
        values = { 'help': self.get_help() }
        issue = self.get_issue(issue_id, post.get('token'))
        
        if issue_id and not issue:
            return request.website.render('website.403', {})
        
        if not issue_id:
            partner = request.env['res.partner'].sudo().create({
                'name': _('Name'),
                'active': True,
                'customer': True,
                'email': post.get('delivery_email'),
                # ~ 'agents': [(6, 0, request.env['res.partner'].sudo().browse(reseller_id))],
                'agents': post.get('consume_name'),
                # ~ 'property_invoice_type': None,
            })
            
            issue = request.env['project.issue'].sudo().create({
                'name': 'New Consumer Application',
                'partner_id': partner.id,
                'project_id': request.env.ref('website_consumer_register.project_consumer_register').id,
                'email_from': partner.email,
            })
            self.set_issue_id(issue.id)
            
            return partner.redirect_token('/consumer_register/%s' %issue.id)
           
        elif request.httprequest.method == 'POST':
            reseller = request.env['res.partner'].sudo().search([('name', '=', post.get('reseller_id'))])

            values = {
                'name': post.get('consumer_name'),
                'email': post.get('delivery_email'),
                'login': ''.join(ch for ch in post.get('consumer_name').lower().replace(" ", "") if ch.isalnum()),
                'reseller_id': reseller.id,
                #'country_id': reseller.country_id.id,
                #'agents': post.get('reseller_id'),
                # ~ 'agents': [(6, 0, request.env['res.partner'].sudo().browse(reseller_id))],
            }
            
            request.registry.get('ir.config_parameter').set_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.allow_uninvited', True)
            
            user_login = request.env['res.users'].sudo().signup(values)[1]
            user = request.env['res.users'].sudo().search([('login', "=", user_login)])
            _logger.warn('~ user %s' % user)
            
            group_dn_sk = request.env.ref('webshop_dermanord.group_dn_sk')
            user.write({'groups_id': [(6, 0, [group_dn_sk.id])]})
            
            try:
                self.update_partner_info(issue, post)
                if action == 'new_contact':
                    return request.redirect('/consumer_register/%s/contact/new' % issue.id)
                
                try:
                    if not user:
                        raise Warning(_("Contact '%s' has no user.") % partner_id)
                    user.action_reset_password()
                    return request.redirect('/consumer_register/%s/thanks' %issue.id)
                except:
                    err = sys.exc_info()
                    error = ''.join(traceback.format_exception(err[0], err[1], err[2]))
                    _logger.exception(_('ERROR: Cannot send mail to %s. Please check your mail server configuration.') % user.name)

            except ValidationError as e:
                try:
                    self.update_partner_info(issue, post)
                except Exception as e:
                    _logger.warn("~ %s" % e)
        else:
            children = self.get_children(issue)
            
        values.update({
            'issue': issue,
            'validation': validation,
            # ~ 'country_selection': [(country['id'], country['name']) for country in request.env['res.country'].search_read([], ['name'])],
            'reseller_selection': [(reseller['id'], reseller['name']) for reseller in request.env['res.partner'].sudo().search([('agent','=',True),('country_id','=',189)])],
            # ~ 'agents':[(reseller['id'], reseller['name']) for reseller in request.env['res.partner'].search([('agent','=',True),('country_id','=',189)]).search_read([], ['name'])],
            'invoice_type_selection': [(invoice_type['id'], invoice_type['name']) for invoice_type in request.env['sale_journal.invoice.type'].sudo().search_read([], ['name'])],
            })
            
        if any(children):
            for k,v in children.items():
                values[k] = v
        
        return request.website.render('website_consumer_register.register_form', values)            

    # can be overrided
    def update_partner_info(self, issue, post):
        values = self.get_consumer_post(post)
        values.pop("login", None)
        
        if post.get('invoicetype'):
            values['property_invoice_type'] = int(post.get('invoicetype'))
        
        issue.partner_id.write(values)
        children_dict = self.get_children_post(issue, post)
        children = children_dict['children']
        
        validation = children_dict['validations']
        
        for field in self.consumer_fields():
            validation['consumer_%s' % field] = 'has-success'

    def find_field_name(self, s):
        return s[(s.index('Field(s) `')+len('Field(s) `')):s.index('` ')]

    @http.route(['/consumer_register/<int:issue_id>/contact/new', '/consumer_register/<int:issue_id>/contact/<int:contact>'], type='http', auth='public', website=True)
    def consumer_contact_new(self, issue_id=None, contact=0, **post):
        help_dic = self.get_help()
        issue = self.get_issue(issue_id, post.get('token'))
        if issue_id and not issue:
            # Token didn't match
            return request.website.render('website.403', {})
        if contact:
            contact = request.env['res.partner'].sudo().browse(contact)
            if not (contact in issue.partner_id.child_ids):
                contact = request.env['res.partner'].sudo().browse([])
        else:
            contact = request.env['res.partner'].sudo().browse([])
        validation = {}
        instruction_contact = ''
        if request.httprequest.method == 'POST':
            instruction_contact = _('Any images or attachments you uploaded have not been saved. Please reupload them.')
            # Values
            values = {f: post['contact_%s' % f] for f in self.contact_fields() if post.get('contact_%s' % f) and f not in ['attachment','image']}

            if post.get('image'):
                image = post['image'].read()
                values['image'] = base64.encodestring(image)
            elif post.get('image_b64'):
                values['image'] = post.get('image_b64')
            values['parent_id'] = issue.partner_id.id
            # multi select
            # ~ category_id = []
            # ~ for c in request.httprequest.form.getlist('category_id'):
                # ~ category_id.append(int(c))
            # ~ values['category_id'] = [(6, 0, category_id)]
            # multi checkbox
            categ_list = []
            for k in post.keys():
                if k.split('_')[0] == 'category':
                    categ_list.append(int(post.get(k)))
            values['category_id'] = [(6, 0, categ_list)]
            # Validation and store
            for field in self.contact_fields():
                if field not in ['attachment','image']:
                    validation['contact_%s' %field] = 'has-success'
            # Check required fields
            for field in ['name', 'email']:
                if not values.get(field):
                    validation['contact_%s' % field] = 'has-error'
            if not 'has-error' in validation.values():
                if contact:
                    contact.sudo().write(values)
                else:
                    if request.env['res.users'].sudo().with_context(active_test = False).search([('login', '=', values.get('email'))]):
                        validation['contact_email'] = 'has-error'
                        contact = request.env['res.partner'].sudo().browse([])
                        help_dic['help_contact_email'] = _('This email aldready exists. Choose another one!')
                        return request.website.render('website_consumer_register.contact_form', {
                            'issue': issue,
                            'contact': contact,
                            'help': help_dic,
                            'validation': validation,
                            'instruction_contact': instruction_contact,
                            'res_partner_category_selection': [(category['id'], category['name']) for category in request.env['res.partner.category'].sudo().search_read([('id', 'in', [7, 16, 20, 29, 34, 35])], ['name'], order='name')],
                            'values': post,
                        })
                    try:
                        template = request.env.ref('website_consumer_register.consumer_template').sudo()
                        user = template.with_context(no_reset_password=True).copy({
                            'name': values.get('name'),
                            'login': values.get('email'),
                            'image': values.get('image'),
                            'active': False,
                        })
                        contact = user.partner_id.sudo()
                        contact.write(values)
                        
                    except Exception as e:
                        err = sys.exc_info()
                        error = ''.join(traceback.format_exception(err[0], err[1], err[2]))
                        _logger.info('Cannot create user %s: %s' % (values.get('name'), error))
                        contact = None
                        request.env.cr.rollback()
                        instruction_contact = _('Something went wrong when creating the contact. Please try again and contact support of error persists. ') + instruction_contact
                if contact:
                    if post.get('attachment'):
                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': post['attachment'].filename,
                            'res_model': 'res.partner',
                            'res_id': contact.id,
                            'datas': base64.encodestring(post['attachment'].read()),
                            'datas_fname': post['attachment'].filename,
                        })
                    return request.redirect('/consumer_register/%s?token=%s' %(issue.id, post.get('token')))
        else:
            issue = request.env['project.issue'].sudo().browse(int(issue))

        return request.website.render('website_consumer_register.contact_form', {
            'issue': issue,
            'contact': contact,
            'customer_no': issue_id,
            # ~ 'agents': [(6,0,request.env['res.partner'].sudo().browse(reseller_id))],
            'agents': 'Skogsro Spa',
            'help': help_dic,
            'validation': validation,
            'instruction_contact': instruction_contact,
            'res_partner_category_selection': [(category['id'], category['name']) for category in request.env['res.partner.category'].sudo().search_read([('id', 'in', [7, 16, 20, 29, 34, 35])], ['name'], order='name')],
            'values': post,
        })

    @http.route(['/consumer_register/<int:issue_id>/contact/<int:contact>/delete'], type='http', auth='public', website=True)
    def consumer_contact_delete(self, issue_id=None, contact=0, **post):
        issue = self.get_issue(issue_id, post.get('token'))
        if issue_id and not issue:
            # Token didn't match
            return request.website.render('website.403', {})
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
        return request.redirect('/consumer_register/%s?token=%s' %(issue.id, issue.partner_id.token))

    @http.route(['/consumer_register/contact/remove_img_contact'], type='json', auth="public", website=True)
    def consumer_contact_remove_img(self, partner_id='0', **kw):
        partner = request.env['res.partner'].browse(int(partner_id))
        if partner:
            partner.write({'top_image': None})
            return True
        return False

    @http.route(['/consumer_register/<int:issue_id>/attachment/<int:attachment>/delete'], type='http', auth='public', website=True)
    def consumer_attachment_delete(self, issue_id=None, attachment=0, **post):
        issue = self.get_issue(issue_id, post.get('token'))
        if issue_id and not issue:
            # Token didn't match
            return request.website.render('website.403', {})
        if attachment > 0:
            attachment = request.env['ir.attachment'].sudo().browse(attachment)
            if attachment.res_model == 'res.partner' and attachment.res_id != 0:
                contact = request.env['res.partner'].browse(attachment.res_id)
                if contact.parent_id == issue.partner_id:
                    attachment.unlink()
                    return request.redirect('/consumer_register/%s/contact/%s?token=%s' %(issue.id, contact.id, issue.partner_id.token))
        return request.redirect('/consumer_register/%s?token=%s' %(issue.id, issue.partner_id.token))

    @http.route(['/website_consumer_register_message_send'], type='json', auth="public", website=True)
    def website_consumer_register_message_send(self, issue_id, msg_body, **kw):
        issue = self.get_issue(issue_id, kw.get('token'))
        if issue_id and not issue:
            # Token didn't match
            return request.website.render('website.403', {})
        if msg_body != '':
            message = request.env['mail.message'].sudo().create({
                'model': 'project.issue',
                'res_id': int(issue_id),
                'type': 'comment',
                'body': msg_body,
                'author_id': issue.partner_id.id
            })
            if message:
                return True
        return False

    @http.route(['/consumer_register/contact/pw_reset'], type='json', auth='public', website=True)
    def contact_pw_reset(self, user_id=0, partner_id=0, **kw):
        _user = request.env['res.users'].sudo().browse(user_id)
        consumer = _user.partner_id
        user = request.env['res.users'].sudo().search([('partner_id', '=', partner_id)])
        try:
            if not user:
                raise Warning(_("Contact '%s' has no user.") % partner_id)
            user.action_reset_password()
            return _(u'Password reset has been sent to user %s by email') % user.name
        except:
            err = sys.exc_info()
            error = ''.join(traceback.format_exception(err[0], err[1], err[2]))
            _logger.exception(_('Cannot send mail to %s. Please check your mail server configuration.') % user.name)
            return _('Cannot send mail to %s. Please check your mail server configuration.') % user.name

    @http.route(['/consumer_register/<int:issue_id>/thanks'], type='http', auth='public', website=True)
    def thanks_for_your_application(self, issue_id=None, **post):
        issue = self.get_issue(issue_id, post.get('token'))
        if issue_id and not issue:
            # Token didn't match
            return request.website.render('website.403', {})
        return request.website.render('website_consumer_register.thanks_for_your_application', {'issue': issue})


class res_users(models.Model):
    _inherit = 'res.users'
    @api.model
    def create(self,values):
        res = super(res_users,self).create(values)
        # ~ values.update({
        # ~ })
        return res
