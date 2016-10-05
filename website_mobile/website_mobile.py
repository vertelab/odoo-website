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
        self.string = string if string else request.env[model].fields_get([field])[field]['string']
        self.value = default_value if default_value else ''
        self.placeholder = planceholder if placeholder else request.env[model].fields_get([field])[field]['string']
        self.required = required if required else request.env[model].fields_get([field])[field]['required']
        self.help = help if help else request.env[model].fields_get([field])[field]['help']
        self.step = step if step else 1
        self.write = True
        self.create = True
        
    def get_value(self,obj):
        if not obj:
             if request.httprequest.args.get(self.name):
                return request.httprequest.args.get(self.name)
        else:
            return obj.read([self.name])[0][self.name]
            
    def get_info(self,obj):
        if not obj:
             if request.httprequest.args.get(self.name):
                return request.httprequest.args.get(self.name)
        else:
            return obj.read([self.name])[0][self.name]
            

    def get_selection(self,obj):
        if self.ttype == 'selection':
            return request.env[self.model].fields_get([self.name])[self.name]['selection']  # add selected
        elif self.ttype == 'Many2one':
            return [('','')]
        else:
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
            obj.unlink()
            return werkzeug.utils.redirect(MODULE_BASE_PATH, 302)


    def do_edit(self,obj=None,**post):        
        if request.httprequest.method == 'GET':
            return request.render(self.template['detail'], {'crud': self, 'object': obj, 'title': obj.name, 'mode': 'edit'})
        else:
            obj.write({f.name: post.get(f.name) for f in self.fields_info if f.write})
            return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name,'mode': 'view'})
  

    def do_add(self,notifications=None,**post):
        if request.httprequest.method == 'GET':
            return request.render(self.template['detail'], {'crud': self, 'object': None, 'notifications': notifications, 'title': 'Add','mode': 'edit'})
        else:
            obj = request.env[self.model].create({f.name: post.get(f.name) for f in self.fields_info if f.create})
            return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name,'mode': 'view'})


    def do_list(self,obj=None,search=None):
        if obj:
            return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name, 'mode': 'view'})
        return request.render(self.template['list'], {'crud': self,'objects': self.search(search=search),'title': 'Module Title'})


