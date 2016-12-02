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

import logging
_logger = logging.getLogger(__name__)


class fts_fts(models.Model):
    _inherit = 'fts.fts'

    facet = fields.Selection(selection_add=[('blog_tag','Blog Tag'),('blog','Blog'),('author','Author')])

    @api.one
    def get_object(self,words):
        if self.res_model == 'blog.post':
            blog = self.env['blog.post'].browse(self.res_id)
            return {'name': blog.name, 'body': self.get_text([blog.name,blog.subtitle,self.content],words)}
        return super(fts_fts, self).get_object()

class Blog(models.Model):
    _inherit = 'blog.post'

    @api.one
    @api.depends('content','website_published','name','subtitle','blog_id','author_id')
    def _full_text_search_update(self):
        if self.website_published:
            self.env['fts.fts'].update_html(self._name,self.id,html=self.content+' '+self.name+' '+self.subtitle,rank=int(self.ranking))
            self.env['fts.fts'].update_text(self._name,self.id,text=self.author_id.name,facet='author',rank=int(self.ranking))
            self.env['fts.fts'].update_text(self._name,self.id,text=self.blog_id.name,facet='blog',rank=int(self.ranking))
            #self.env['fts.fts'].update_text(self._name,self.id,text=' '.join([self.])self.blog_id.name,facet='blog_tag',rank=int(self.ranking))
            # SEO metadata ????
        self.full_text_search_update = ''

    full_text_search_update = fields.Char(compute="_full_text_search_update",store=True)



