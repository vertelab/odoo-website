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
    _inherit = 'ir.attachment'

    @api.one
    @api.depends('index_content','name','description')
    def _full_text_search_update(self):
        self.env['fts.fts'].update_text(self._name,self.id,html=self.index_content or ''+' '+self.name+' '+self.description or '')
        self.full_text_search_update = ''
        if 'document' in self.file_type:
            self.env['fts.fts'].update_text(self._name,self.id,text=self.name,facet='document')
        if 'image' in self.file_type:
            self.env['fts.fts'].update_text(self._name,self.id,text=self.name,facet='image')
        # Exif metadata ????

    full_text_search_update = fields.Char(compute="_full_text_search_update",store=True)



