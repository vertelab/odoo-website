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

from openerp import models, fields, api, _
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website_blog.controllers.main import QueryURL, WebsiteBlog

import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'
    
    def get_kw_blog(self, kw):
        return kw['blog'].name if kw.get('blog', None) else ''

class CachedBlog(WebsiteBlog):
    
    #~ @http.route([
        #~ '/blog',
        #~ '/blog/page/<int:page>',
    #~ ], type='http', auth="public", website=True)

    @memcached.route(
        flush_type=lambda kw: 'blog-list',
        key=lambda kw: '{db},/blog/page/%s,{employee},{logged_in},{publisher},{designer},{lang} %s' % (
            kw.get('page', 1),
            (request.env['blog.post'].search_read(
                [('website_published', '=', True), ('memcached_time', '!=', False)],
                ['memcached_time'], limit=1, order='memcached_time desc'
            ) or [{'memcached_time': ''}])[0]['memcached_time']
        )
    )
    def blogs(self, page=1, **post):
        return super(CachedBlog, self).blogs(page, **post)
        

    #~ @http.route([
        #~ '/blog/<model("blog.blog"):blog>',
        #~ '/blog/<model("blog.blog"):blog>/page/<int:page>',
        #~ '/blog/<model("blog.blog"):blog>/tag/<model("blog.tag"):tag>',
        #~ '/blog/<model("blog.blog"):blog>/tag/<model("blog.tag"):tag>/page/<int:page>',
    #~ ], type='http', auth="public", website=True)
    @memcached.route(
        flush_type=lambda kw: 'blog %s' %request.website.get_kw_blog(kw),
        key=lambda kw: '{db},/blog/%s/tag/%s/page/%s,{employee},{logged_in},{publisher},{designer},{lang} %s' % (
            kw.get('blog') and kw['blog'].id or 0,
            kw.get('tag') and kw['tag'].id or 0,
            kw.get('page', 1),
            (kw.get('blog') and request.env['blog.post'].search_read(
                [('website_published', '=', True), ('memcached_time', '!=', False), ('blog_id', '=', kw['blog'].id)],
                ['memcached_time'], limit=1, order='memcached_time desc' 
            ) or [{'memcached_time': ''}])[0]['memcached_time']
        )
    )
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog, tag, page, **opt)


    #~ @http.route([
            #~ '''/blog/<model("blog.blog"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    #~ ], type='http', auth="public", website=True)
    @memcached.route(
        flush_type=lambda kw: 'blog %s' %request.website.get_kw_blog(kw),
        key=lambda kw: '{db},/blog/%s/post/%s,{employee},{logged_in},{publisher},{designer},{lang} %s' % (
            kw.get('blog') and kw['blog'].id or 0,
            kw.get('blog_post') and kw['blog_post'].id or 0,
            kw.get('blog_post') and kw['blog_post'].memcached_time or ''
        )
    )
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        return super(CachedBlog, self).blog_post(blog, blog_post, tag_id, page, enable_editor, **post)

class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    memcached_time = fields.Datetime(string='Memcached Timestamp', default=lambda *args, **kwargs: fields.Datetime.now(), help="Last modification relevant to memcached.")
    
    @api.one
    def do_publish(self):
        super(BlogPost, self).do_publish()
        self.memcached_time = fields.Datetime.now()

    @api.one
    def do_unpublish(self):
        super(BlogPost, self).do_unpublish()
        self.memcached_time = fields.Datetime.now()
    
    @api.multi
    def write(self, values):
        for field in self.get_memcached_fields():
            if field in values:
                values['memcached_time'] = fields.Datetime.now()
                break
        return super(BlogPost, self).write(values)
    
    @api.model
    def get_memcached_fields(self):
        """Return a list of fields that should trigger an update of memcached."""
        return ['website_published', 'name', 'content', 'tag_ids', 'blog_id', 'security_type', 'group_ids', 'object_ids', 'website_meta_title', 'website_meta_keywords']
