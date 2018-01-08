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


    # '/blog'
    @memcached.route(max_age=600)
    def blogs(self, page=1, **post):
        return super(CachedBlog, self).blogs(page, **post)

    # '/blog/<model("blog.blog"):blog>'
    @memcached.route(max_age=600)
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog, tag, page, **opt)

    # '/blog/<model("blog.blog"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>'
    @memcached.route(key=lambda : '{path},{logged_in}')
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        return super(CachedBlog, self).blog_post(blog, blog_post, tag_id, page, enable_editor, **post)

    # '/blogpost/comment'
    @memcached.route(key=lambda : '{path},{logged_in}')
    def blog_post_comment(self, blog_post_id=0, **post):
        return super(CachedBlog, self).blog_post_comment(blog_post_id, **post)

    # '/blogpost/get_discussion/'
    @memcached.route(key=lambda : '{path},{logged_in}')
    def discussion(self, post_id=0, path=None, count=False, **post):
        return super(CachedBlog, self).discussion(post_id, path, count, **post)

    # '/blogpost/get_discussions/'
    @memcached.route(key=lambda : '{path},{logged_in}')
    def discussions(self, post_id=0, paths=None, count=False, **post):
        return super(CachedBlog, self).discussions(post_id, paths, count, **post)

    # '/blog/get_user/'
    @memcached.route(key=lambda : '{path},{logged_in}')
    def get_user(self, **post):
        return super(CachedBlog, self).get_user(**post)

    # '/blogpost/post_discussion'
    @memcached.route(key=lambda : '{path},{logged_in}')
    def post_discussion(self, blog_post_id, **post):
        return super(CachedBlog, self).post_discussion(blog_post_id, **post)
