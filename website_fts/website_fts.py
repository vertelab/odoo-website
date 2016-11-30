# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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

from openerp import models, fields, api, _
from openerp import http
from openerp.http import request
from datetime import datetime
import werkzeug

#from openerp.addons.website_fts.html2text import html2text

import logging
_logger = logging.getLogger(__name__)

class fts_fts(models.Model):
    _name = 'fts.fts'
    _order = "name, rank, count"
    

    name = fields.Char(index=True)
    res_model = fields.Many2one(comodel_name='ir.model')
    res_id    = fields.Integer()
    count = fields.Integer(default=1)
    rank = fields.Integer(default=10)
    group_ids = fields.Many2many(comodel_name="res.groups")
    
    @api.one
    @api.depends('res_model','res_id')
    def _model_record(self):
        if self.res_model and self.res_id and self.env[self.res_model].browse(self.res_id):
            self.model_record = self.env[self.res_model].browse(self.res_id)
    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].search([('state', '!=', 'manual')])
#        return self.env[self.model].browse(self.res_id)
        return [(model.model, model.name)
                for model in models
                if not model.model.startswith('ir.')]    
    #~ model_record = fields.Reference(string="Record",selection="_reference_models",compute="_model_record",store=True,index=True)
    #~ model_name = fields.Char(string="Model Name",related="model_record.name")
    model_type = fields.Char(string="Model Type",related="res_model.name")

    @api.one
    def update_html(self,res_model,res_id,html):
        self.env['fts.fts'].search([('res_model','=',res_model),('res_id','=',res_id)]).unlink()
        
        pass
    #~ if html2text:
        #~ html = html2text(html.decode('utf-8')).encode('utf-8')
        #~ html = self._removeSymbols(html.decode('utf-8'), '[', ']').encode('utf-8')
        #~ html = self._removeSymbols(html.decode('utf-8'), '\n').encode('utf-8')
        #~ html = self._removeSymbols(html.decode('utf-8'), '#').encode('utf-8')

    
    
    #~ def _removeSymbols(self, html_txt, symbol1, symbol2=False):

        #~ if not symbol1 and not symbol2:
            #~ return html_txt

        #~ # Function to eliminate text between: symbol1 and symbol2
        #~ index=html_txt.find(symbol1)
        #~ start=0
        #~ txt=''
        #~ while index>0:
            #~ if symbol2:
                #~ index2=html_txt.find(symbol2, index)
                #~ if index2<=0:
                    #~ break
            #~ else:
                #~ index2=index+len(symbol1)-1
            #~ txt+=html_txt[start:index]
            #~ start=index2+1
            #~ index=html_txt.find(symbol1, start)

        #~ if len(txt)==0:
            #~ return html_txt

        #~ return txt


