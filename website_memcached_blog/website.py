# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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


from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website_blog.controllers.main import QueryURL, WebsiteBlog

import logging
_logger = logging.getLogger(__name__)

class CachedBlog(WebsiteBlog):
    
    @memcached.route(max_age=600,add_key=True)
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog,tag,page,**opt)
    
    @memcached.route(key=lambda : '{path},{logged_in}')
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        return super(CachedBlog, self).blog_post(blog,blog_post,tag_id,page,enable_editor,**post)