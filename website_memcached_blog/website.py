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
    memcached_time = fields.Datetime(string='Memcached Timestamp', default=lambda *args, **kwargs: fields.Datetime.now(), help="Last modification relevant to memcached.")


    #~ @http.route([
        #~ '/blog',
        #~ '/blog/page/<int:page>',
    #~ ], type='http', auth="public", website=True)

    @memcached.route(flush_type=lambda kw: 'blog-list', key=lambda kw: '{db}/blog/page/%s{employee}{logged_in}{publisher}{designer}{lang}%s' % (kw.get('page', 1),
        request.env['blog.blog'].search_read(
            [('website_published', '=', True), ('memcached_time', '!=', False)],
            ['memcached_time'], limit=1, order='memcached_time desc' ) or {'memcached_time': ''} )['memcached_time'])
    
    def blogs(self, page=1, **post):
        return super(CachedBlog, self).blogs(page, **post)
        

    #~ @http.route([
        #~ '/blog/<model("blog.blog"):blog>',
        #~ '/blog/<model("blog.blog"):blog>/page/<int:page>',
        #~ '/blog/<model("blog.blog"):blog>/tag/<model("blog.tag"):tag>',
        #~ '/blog/<model("blog.blog"):blog>/tag/<model("blog.tag"):tag>/page/<int:page>',
    #~ ], type='http', auth="public", website=True)
    @memcached.route(flush_type=lambda kw: 'blog %s' %request.website.get_kw_blog(kw))
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog, tag, page, **opt)


    #~ @http.route([
            #~ '''/blog/<model("blog.blog"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    #~ ], type='http', auth="public", website=True)
    @memcached.route(flush_type=lambda kw: 'blog %s' %request.website.get_kw_blog(kw))
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        return super(CachedBlog, self).blog_post(blog, blog_post, tag_id, page, enable_editor, **post)
        
        

    #~ @http.route(['/blogpost/comment'], type='http', auth="public", website=True)
    #~ @memcached.route()
    #~ def blog_post_comment(self, blog_post_id=0, **post):
        #~ return super(CachedBlog, self).blog_post_comment(blog_post_id, **post)

    #~ @http.route([
        #~ '/mcflush/blog',
    #~ ], type='http', auth="user", website=True)
    #~ def memcached_flush_blog(self,**post):
        #~ return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='blog'),'Flush Blog','/mcflush/blog'))

    #~ @http.route([
        #~ '/mcflush/blog/all',
    #~ ], type='http', auth="user", website=True)
    #~ def memcached_flush_blog_all(self,**post):
        #~ memcached.MEMCACHED_CLIENT().delete(memcached.get_keys(flush_type='blog'))
        #~ return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='blog'),'Flush Blog','/mcflush/blog'))
            
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
        values['memcached_time'] = fields.Datetime.now()
        return super(BlogPost, self).write(values)
