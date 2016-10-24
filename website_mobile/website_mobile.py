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
import pytz

import logging
_logger = logging.getLogger(__name__)

class website(models.Model):
    _inherit = 'website'

    @api.multi
    def convert_to_local(self, timestamp, tz_name=None):
        if not tz_name:
            tz_name = self._context.get('tz') or self.env.user.tz
        dt = fields.Datetime.from_string(timestamp)
        local_dt = pytz.utc.localize(dt).astimezone(pytz.timezone(tz_name))
        return fields.Datetime.to_string(local_dt)

    @api.multi
    def convert_to_utc(self, timestamp, tz_name=None):
        if not tz_name:
            tz_name = self._context.get('tz') or self.env.user.tz
        dt = fields.Datetime.from_string(timestamp)
        utc_dt = pytz.timezone(tz_name).localize(dt).astimezone(pytz.utc)
        return fields.Datetime.to_string(utc_dt)


class mobile_input_field(object):
    # type is the input widget type, ttype is the field type
    def __init__(self,model,field,type=None,ttype=None,string=None,default_value=None,placeholder=None,required=None,help=None,step=None):
        self.model = model
        self.child_class = None
        self.name = field
        self.ttype = ttype if ttype else request.env[model].fields_get([field])[field]['type']
        self.relation = None
        if type:
            self.type = type
        elif self.ttype in ['date', 'datetime']:
            self.type = self.ttype
        elif self.ttype in ['float', 'integer']:
            self.type = 'number' if self.name != 'id' else 'hidden'
        elif self.ttype == 'boolean':
            self.type = 'boolean'
        elif self.ttype in ['selection', 'many2one']:
            self.type = 'selection'
        elif self.ttype in ['one2many', 'many2many']:
            self.type = 'table'
            self.relation = request.env[model].fields_get([field])[field]['relation']
        elif 'mail' in field:
            self.type = 'email'
        else:
            self.type = 'text'
        # text, password, datetime, datetime-local, date, month, time, week, number, email, url, search, tel, color  (select,textarea, checkbox, radio)
        self.string = string if string else request.env[model].fields_get([field])[field]['string']
        self.value = default_value if default_value else ''
        self.placeholder = planceholder if placeholder else request.env[model].fields_get([field])[field]['string']
        self.required = required if required else request.env[model].fields_get([field])[field]['required']
        self.help = help if help else (request.env[model].fields_get([field])[field]['help'] if 'help' in request.env[model].fields_get([field])[field] else '')
        self.step = step if step else 1  # Numeriskt
        self.write = True if self.name != 'id' else False
        self.create = True

    def get_post_value(self, post):
        if self.ttype in ['char', 'text', 'html']:
            return post.get(self.name, '')
        elif self.ttype in ['integer', 'many2one']:
            return int(post.get(self.name, None)) if post.get(self.name, '') != '' else None
        elif self.ttype == 'float':
            return float(post.get(self.name, None)) if post.get(self.name, '') != '' else None
        elif self.ttype == 'boolean':
            return True if post.get(self.name) in ['True', '1'] else False
        elif self.ttype == 'date':
            return post.get(self.name, fields.Date.today())
        elif self.ttype == 'datetime':
            return post.get(self.name, fields.Datetime.now())
        else:
            raise Warning('Unknow type')

    def get_form_value(self, form, index):
        if self.ttype in ['char', 'text', 'html']:
            return form.get(self.name)[index]
        elif self.ttype in ['integer', 'many2one']:
            return int(form.get(self.name)[index] if form.get(self.name)[index] else 0)
        elif self.ttype == 'float':
            return float(form.get(self.name)[index] if form.get(self.name)[index] else 0.0)
        elif self.ttype == 'boolean':
            return True if form.get(self.name)[index] in ['True', '1'] else False
        elif self.ttype == 'date':
            return form.get(self.name)[index] if form.get(self.name)[index] else fields.Date.today()
        elif self.ttype == 'datetime':
            return form.get(self.name)[index] if form.get(self.name)[index] else fields.Datetime.now()
        else:
            raise Warning('Unknow type')

    def get_value(self,obj):
        if not obj:
            if request.httprequest.args.get(self.name):
                if self.ttype in ['char', 'text', 'html']:
                    return request.httprequest.args.get(self.name, '')
                elif self.ttype in ['integer', 'many2one']:
                    return int(request.httprequest.args.get(self.name, None)) if request.httprequest.args.get(self.name, '') != '' else None
                elif self.ttype == 'float':
                    return float(request.httprequest.args.get(self.name, None)) if request.httprequest.args.get(self.name, '') != '' else None
                elif self.ttype == 'boolean':
                    return True if request.httprequest.args.get(self.name) in ['True', '1'] else False
                elif self.ttype == 'date':
                    return request.httprequest.args.get(self.name, fields.Date.today())
                elif self.ttype == 'datetime':
                    return request.httprequest.args.get(self.name, fields.Datetime.now())
                else:
                    raise Warning('Unknow type')
            return None
        else:
            if self.ttype == 'many2one':
                if obj.read([self.name])[0][self.name]:
                    return obj.read([self.name])[0][self.name][0]
                else:
                    return None
            elif self.ttype in ['one2many', 'many2many']:
                return obj.env[self.relation].browse(obj.read([self.name])[0][self.name])
            else:
                return obj.read([self.name])[0][self.name]

    def get_selection_value(self,obj):
        if not obj:
             if request.httprequest.args.get(self.name):
                return request.httprequest.args.get(self.name)
        else:
            if self.ttype == 'many2one':
                if obj.read([self.name])[0][self.name]:
                    return obj.read([self.name])[0][self.name][1]
                else:
                    return None
            else:
                if obj.read([self.name])[0][self.name]:
                    return [x for x in self.get_selection(obj) if x[0] == obj.read([self.name])[0][self.name]][0][1]
                else:
                    return None

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
            dropdown_list = [(None, None)]
            for r in request.env[self.model].fields_get([self.name])[self.name]['selection']:
                dropdown_list.append(r)
            return dropdown_list  # add selected
        elif self.ttype == 'many2one':
            dropdown_list = [(None, None)]
            record_list = request.env[request.env[self.model].fields_get([self.name])[self.name]['relation']].search([]) # a list of records related to this filed
            for r in record_list:
                dropdown_list.append((r.id, r.name))
            return dropdown_list
        else:  # Many2many should be a multi selection
            return [(None, None)]

class mobile_crud(http.Controller):

    def __init__(self):
        self.model = ''
        self.root = '/'
        self.search_domain = []
        self.fields_info = [mobile_input_field(self.model, 'id')]
        self.template = {'list': 'website_mobile.list', 'detail': 'website_mobile.detail', 'detail_grid': 'website_mobile.detail_grid'}
        #~ self.template = {'list': '%s.object_list' % __name__, 'detail': '%s.object_detail' % __name__}
        self.limit = 25
        self.order = 'name'
        self.form_type = ''  # Basic=='' / form-inline / form-horizontal http://getbootstrap.com/css/#forms-example
        self.input_size = 'input-lg' # input-lg, input-sm http://getbootstrap.com/css/#forms-control-sizes
        self.col_size_edit = '12'
        self.col_size_view = '12'
        self.button_size = 'btn-lg' # btn-lg, btn-sm, btn-xs
                        # tuple(id, link, icon_name)
        self.footer_icons = [('home_button','#','fa fa-home'),('add_button','add','fa fa-plus')]
        self.footer_list = None
        self.footer_view = None
        self.footer_edit = None

    def load_fields(self,fields):
        for f in fields:
            self.fields_info.append(mobile_input_field(self.model, f))

    def search(self,search=None,domain=None):
        if not domain:
            domain = list(self.search_domain)
        if search:
            domain.append(('name','ilike',search))
        return request.env[self.model].sudo().search(domain, order=self.order, limit=self.limit)

#
#
#  Methods for crud
#

    def do_delete(self,obj=None,base_path='/'):
        if obj:
            try:
                obj.unlink()
                return werkzeug.utils.redirect(base_path, 302)
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
                    _logger.debug({f.name: f.get_post_value(post) for f in self.fields_info})
                    obj.write({f.name: f.get_post_value(post) for f in self.fields_info if f.write})
                    request.context['alerts']=[{'subject': _('Saved'),'message':_('The record is saved'),'type': 'success'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name,'mode': 'view'})
                except Exception as e:
                    request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not saved\n%s') %(e),'type': 'error'}]
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
                    _logger.debug({f.name: f.get_post_value(post) for f in self.fields_info})
                    obj = request.env[self.model].create({f.name: f.get_post_value(post) for f in self.fields_info if f.create})
                    request.context['alerts'] = [{'subject': _('Saved'),'message':_('The record is saved'),'type': 'success'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': obj,'title': obj.name,'mode': 'view'})
                except Exception as e:
                    request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not saved\n%s') %(e),'type': 'error'}]
                    return request.render(self.template['detail'], {'crud': self, 'object': None, 'title': None, 'mode': 'edit'})


    def do_list(self,obj=None,search=None,domain=None,alerts=None):
        if obj:
            return request.render(self.template['detail'], {'crud': self, 'object': obj,'alerts': alerts,'title': obj.name, 'mode': 'view'})
        return request.render(self.template['list'], {'crud': self,'objects': self.search(search=search,domain=domain),'title': 'Module Title'})

    def do_grid(self, obj_ids=None, alerts=None):
        if request.httprequest.method == 'GET':
            return request.render(self.template['detail_grid'], {'crud': self, 'objects': obj_ids or [], 'title': 'Grid', 'mode': 'edit_grid'})
        else:
            form_data = request.httprequest.form
            form = {}
            for f in request.httprequest.form:
                form[f] = form_data.getlist(f)
            try:
                self.validate_form()
            except Exception as e:
                return request.render(self.template['detail_grid'], {'crud': self, 'objects': obj_ids, 'title': 'Grid', 'mode': 'edit_grid'})
            else:
                try:
                    ids = []
                    for i in form['id']:
                        ids.append(int(i))
                    i = 0
                    for obj in request.env[self.model].browse(ids):
                        obj.write({ f.name: f.get_form_value(form, i) for f in self.fields_info if f.write })
                        i += 1
                    request.context['alerts']=[{'subject': _('Saved'),'message':_('The record is saved'),'type': 'success'}]
                    return request.render(self.template['detail_grid'], {'crud': self, 'objects': obj_ids, 'title': 'Grid', 'mode': 'view'})
                except Exception as e:
                    request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not saved\n%s') %(e),'type': 'error'}]
                    return request.render(self.template['detail_grid'], {'crud': self, 'objects': obj_ids, 'title': 'Grid', 'mode': 'edit_grid'})


    @http.route(['/grid_delete'],type='json', auth="user", website=True)
    def do_grid_delete(self, obj=None, **kw):
        if obj:
            try:
                record = request.env[obj.rpartition('(')[0]].browse(int(obj.partition('(')[-1].rpartition(',')[0]))
                record.unlink()
                request.context['alerts']=[{'subject': _('Saved'),'message':_('The record has been deleted'),'type': 'success'}]
                return 'grid_obj_deleted'
            except:  # Catch exception message
                request.context['alerts']=[{'subject': _('Error'),'message':_('The record is not deleted'),'type': 'error'}]
                return None


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


