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

BASE = 'Kalle'

class mobile_crud(http.Controller):
    
    def __init__(self):
        self.model = 'res.partner'
        self.search_domain = [('type','=','contact')]
        self.fields =  ['name','is_company','phone','email','type']
        self.fields_info = {'is_company': {'type': 'hidden','default': 'true'}}
        self.template = {'list': '%s.object_list' % __name__, 'detail': '%.object_detail' % __name__}
        self.limit = 25
        self.order = 'name'
        self.notifications = []  # list of dicts message, type, action_one, action_two 


    def do_action(self,action=['edit','add','delete','search'],obj=None,search=None,**post,request):
        
        if request.httprequest.url[-4:] == 'edit' and 'edit' in action: #Edit
            if request.httprequest.method == 'GET':
                return request.render(self.template['detail'], {'model': self.model, 'object': obj, 'fields': self.fields, 'root': MODULE_BASE_PATH, 'title': obj.name, 'db': request.db, 'mode': 'edit'})
            else:
                obj.write({
                    f: post.get(f) for f in self.fields
                })
                return request.render(self.template['detail'], {'model': self.model, 'object': obj, 'fields': self.fields, 'root': MODULE_BASE_PATH, 'title': obj.name, 'db': request.db, 'mode': 'view'})
        elif request.httprequest.url[-3:] == 'add' and 'add' in action: #Add
            if request.httprequest.method == 'GET':
                return request.render(self.template['detail'], {'model': self.model, 'object': None, 'fields': self.fields, 'root': MODULE_BASE_PATH, 'title': 'Add User', 'db': request.db,'mode': 'add'})
            else:
                record = { f: post.get(f) for f in self.fields }
                partner = request.env[self.model].create(record)
                return request.render(self.template['detail'], {'model': self.model, 'object': obj, 'fields': self.fields, 'root': MODULE_BASE_PATH, 'title': obj.name, 'db': request.db, 'mode': 'view'})
        elif request.httprequest.url[-6:] == 'delete' and 'delete' in action: #Delete
            if obj:
                obj.unlink()
                return werkzeug.utils.redirect(MODULE_BASE_PATH, 302)
        elif request.httprequest.url[-6:] == 'search': #Search
            if request.httprequest.method == 'POST':
            self.search_domain.append(('name','ilike',post.get('search_words')))
        elif obj:  # Detail
            return request.render(self.template['detail'], {'model': self.model, 'object': obj, 'fields': self.fields, 'root': MODULE_BASE_PATH, 'title': obj.name, 'db': request.db, 'mode': 'view'})
        return request.render(self.template['list'], {
            'objects': self.search(search=post.get('search_word'),request),
            'title': MODULE_TITLE,
            'root': MODULE_BASE_PATH,
            'db': request.db,
        })

    def search(self,search=None,request):
        if search:
            self.search_domain.append(('name','ilike',search))
        return request.env[self.model].search(self.search_domain, order=self.order, limit=self.limit)
