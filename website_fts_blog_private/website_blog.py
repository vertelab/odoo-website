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


class Blog(models.Model):
    _inherit = 'blog.post'

    @api.one
    def _full_text_search_update(self):
        self._full_text_search_delete()
        self.fts_dirty = False
        if self.website_published:
            self.env['fts.fts'].update_html(self._name, self.id, html=self.content+' '+self.name+' '+self.subtitle,rank=int(self.ranking),groups=self.group_ids if self.group_ids else self.blog_id.group_ids or None)
            self.env['fts.fts'].update_text(self._name, self.id, text=self.author_id.name,facet='author',rank=int(self.ranking),groups=self.group_ids if self.group_ids else self.blog_id.group_ids or None)
            self.env['fts.fts'].update_text(self._name, self.id, text=self.blog_id.name, facet='blog', rank=int(self.ranking),groups=self.group_ids if self.group_ids else self.blog_id.group_ids or None)
            #self.env['fts.fts'].update_text(self._name,self.id,text=' '.join([self.])self.blog_id.name,facet='blog_tag',rank=int(self.ranking))
            # SEO metadata ????




