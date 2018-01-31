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

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class fts_fts(models.Model):
    _inherit = 'fts.fts'

    facet = fields.Selection(selection_add=[('document','Document'),('image','Image')])

    @api.one
    def get_object(self,words):
        if self.res_model == 'ir.attachment':
            page = self.env['ir.attachment'].browse(self.res_id)
            return {'name': page.name, 'body': self.get_text([self.description,page.index_context],words)}
        return super(fts_fts, self).get_object()

class document_file(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'fts.model']


    group_ids = fields.Many2many(string='Groups', comodel_name='res.groups')

    _fts_fields = ['index_content','name','description']
    _fts_fields_d = [{'name': 'index_content'}, {'name': 'name'}, {'name': 'description'}]

    @api.depends('index_content','name','description')
    @api.one
    def _compute_fts_trigger(self):
        """
        Dummy field to trigger the updates on SQL level. Tracking
        changes is much easier on Odoo level than on SQL level. Make
        this field dependant on the relevant fields.
        """
        # TODO: Trigger this update when relevant translations change.
        if self._fts_trigger:
            self._fts_trigger = True
        else:
            self._fts_trigger = False

    @api.one
    def _full_text_search_update(self):
        if self.url and (self.url.startswith('/web/js/') or self.url.startswith('/web/css/')):
            return
        super(document_file, self)._full_text_search_update()
        self.env['fts.fts'].update_html(self._name, self.id, html=' '.join([h for h in [self.index_content, self.name, self.description] if h]), groups=self.group_ids, rank=10)
        if self.file_type and 'document' in self.file_type:
            self.env['fts.fts'].update_text(self._name,self.id,text=self.name,facet='document',groups=self.group_ids, rank=0)
        if self.file_type and 'image' in self.file_type:
            self.env['fts.fts'].update_text(self._name,self.id,text=self.name,facet='image',groups=self.group_ids, rank=0)
        # Exif metadata ????


