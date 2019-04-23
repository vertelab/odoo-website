# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017 Vertel AB (<http://vertel.se>).
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

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# REMOVING HTML-TAGGS FROM (SEO) CONTENT FIELD:
from bs4 import BeautifulSoup

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class BlogPost(models.Model):
    _inherit = 'blog.post'

    @api.multi
    def write(self, values):
        # ~ if 'name' in values.keys():
            # ~ website = self.env['website'].search([], limit = 1)
            # ~ title = website.name.upper() if not website.name == 'localhost' else website.company_id.name.upper()
            # ~ values['website_meta_title'] = values['name'][:55 - len(title)] + " | " + title
        if 'content' in values.keys():
            soup = BeautifulSoup(values['content'], 'html.parser')
            values['website_meta_description'] = soup.get_text()[:152] + '...' 
        if 'tag_ids' in values.keys():
            # ~ _logger.warn('tag_ids %s, sdrKeywords %s' % (values['tag_ids'], values['tag_ids'][0][2]) )
            strKeyword = ", ".join( self.env['blog.tag'].browse(values['tag_ids'][0][2]).mapped('name') )
            values['website_meta_keywords'] = strKeyword
        res = super(BlogPost, self).write(values)
        return res



