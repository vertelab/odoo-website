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
    _name = 'blog.post'
    _inherit = ['blog.post', 'fts.model']

    
    def _get_fts_fields(self):
        return [
            {'name': 'name', 'weight': 'A'},
            {'name': 'subtitle', 'weight': 'A'},
            {'name': 'blog_id.name', 'weight': 'A', 'related': 'blog_id.name', 'related_table': 'blog_blog'},
            {'name': 'author_id.name', 'weight': 'A', 'related': 'author_id.name', 'related_table': 'res_partner'},
            {'name': 'content', 'weight': 'C'},
        ]

    @api.multi
    def fts_search_suggestion(self):
        """
        Return a search result for search_suggestion.
        """
        return {
            'res_id': self.id,
            'model_record': self._name,
            'name': self.name_get()[0][1],
            'blog_id': self.blog_id.id,
        }
