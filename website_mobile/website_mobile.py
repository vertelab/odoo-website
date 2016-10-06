# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
import werkzeug

import logging
_logger = logging.getLogger(__name__)


class mobile_input_field(object):
    def __init__(self,model,field,type=None,ttype=None,string=None,default_value=None,placeholder=None,required=None,help=None,step=None):
        self.model = model
        self.name = field
        self.ttype = ttype if ttype else request.env[model].fields_get([field])[field]['type']
        if type:
            self.type = type
        elif self.ttype in ['date', 'datetime']:
            self.type = 'date'
        elif self.ttype in ['float', 'integer']:
            self.type = 'number'
        elif self.ttype == 'boolean':
            self.type = 'boolean'
        elif 'mail' in field:
            self.type = 'email'
        else:
            self.type = 'text'
        # text, password, datetime, datetime-local, date, month, time, week, number, email, url, search, tel, color  (select,textarea, checkbox, radio)
        self.string = string if string else request.env[model].fields_get([field])[field]['string']
        self.value = default_value if default_value else ''
        self.placeholder = planceholder if placeholder else request.env[model].fields_get([field])[field]['string']
        self.required = required if required else request.env[model].fields_get([field])[field]['required']
        self.help = help if help else request.env[model].fields_get([field])[field]['help']
        self.step = step if step else 1  # Numeriskt
        self.write = True
        self.create = True
       
        
    def get_value(self,obj):
        if not obj:
             if request.httprequest.args.get(self.name):
                return request.httprequest.args.get(self.name)
        else:
            return obj.read([self.name])[0][self.name]

# server-side-controls
# focus, disabled, validation  has-warning, has-error, has-success,  
# http://getbootstrap.com/css/#forms-help-text
    def state(self):
        if request.context.get('form_state',{}).get(self.name):
            return request.context.get('form_state',{}).get(self.name,{})
        else:
            return {}

    def get_selection(self,obj):
        if self.ttype == 'selection':
            return request.env[self.model].fields_get([self.name])[self.name]['selection']  # add selected
        elif self.ttype == 'Many2one':
            return [('','')]
        else:  # Many2many should be a multi selection
            return [(None,None)]

class mobile_crud(http.Controller):
    
    def __init__(self):
        self.model = 'res.partner'
        self.search_domain = [('type','=','contact')]
        self.load_fields(['name','is_company','phone','email','type'])
        #self.fields_info = {'is_company': {'type': 'hidden','default': 'true'}}
        self.template = {'list': 'website_mobile.list', 'detail': 'website_mobile.detail'}
        #~ self.template = {'list': '%s.object_list' % __name__, 'detail': '%s.object_detail' % __name__}
        self.limit = 25
        self.order = 'name'
        self.form_type = ''  # Basic=='' / form-inline / form-horizontal http://getbootstrap.com/css/#forms-example
        self.input_size = 'input-lg' # input-lg, input-sm http://getbootstrap.com/css/#forms-control-sizes
        self.button_size = 'btn-lg' # btn-lg, btn-sm, btn-xs
        self.footer_icons = [('home','','fa-home'),('add','add','fa-plus'),('search_button','','fa-search')]
        self.footer_list = None
        self.footer_view = None
        self.footer_edit = None
        

    def load_fields(self,fields):
        self.fields_info = []
        for f in fields:
            self.fields_info.append(mobile_input_field(self.model,f))


    def search(self,search=None):
        if search:
            self.search_domain.append(('name','ilike',search))
        return request.env[self.model].sudo().search(self.search_domain, order=self.order, limit=self.limit)

#
#
#  Methods for crud
#

    def do_delete(self,obj=None):        
        if obj:
            try:
                obj.unlink()
                return werkzeug.utils.redirect(MODULE_BASE_PATH, 302)
            except:  # Catch exception message
                request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not deleted'),'type': 'error'}]
                return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'edit'})
            

    def do_edit(self,obj=None,**post):        
        if request.httprequest.method == 'GET':
            return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'edit'})
        else:
            try:
                self.validate_form()
            except Exception as e:
                return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'edit'})
            else:
                try: 
                    obj.write({f.name: post.get(f.name) for f in self.fields_info if f.write})
                    request.context['alerts']=[{'subject': _('Saved'),'message':_('The record is saved'),'type': 'success'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name,'mode': 'view'})
                except: # Catch exception message
                    request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not saved'),'type': 'error'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'edit'})
  

    def do_add(self,alerts=None,**post):
        if request.httprequest.method == 'GET':
            return request.render(self.template['detail'], {'crud': self, 'object': None, 'title': 'Add','mode': 'edit'})
        else:
            try:
                self.validate_form()
            except Exception as e:
                return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name, 'mode': 'edit'})
            else:
                try:
                    obj = request.env[self.model].create({f.name: post.get(f.name) for f in self.fields_info if f.create})
                    request.context['alerts'] = [{'subject': _('Saved'),'message':_('The record is saved'),'type': 'success'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name,'mode': 'view'})
                except: # Catch exception message
                    request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not saved'),'type': 'error'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'edit'})

    def do_list(self,obj=None,search=None,alerts=None):
        if obj:
            return request.render(self.template['detail'], {'crud': self, 'object': obj,'alerts': alerts,'title': obj.name, 'mode': 'view'})
        return request.render(self.template['list'], {'crud': self,'objects': self.search(search=search),'title': 'Module Title'})

###############

    def validate_form(self):
        return True
        request.context['alerts'] = [{'subject': _('Alert'),'message':_('Validation are done'),'type': 'danger'}]
        request.context['form_state'] = {'name': {'validation': 'has-warning','help': _('name already taken')}}  # focus ?
        raise Exception(request.context)
        
        
# Alerts http://getbootstrap.com/components/#alerts-examples
#  alerts = [
#              {
#               'subject': '..',
#               'message': '..',
#               'type': 'success,info,warning,danger',
#               'dismissible': True,
#               'link': '...',
#               'fade-out': nn (sec),
#
#           },]


