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

from openerp.addons.website.controllers.main import Website

import logging
_logger = logging.getLogger(__name__)

    
class CachedWebsite(Website):

    #~ @http.route('/page/<page:page>', type='http', auth="public", website=True)
    @memcached.route(flush_type='page')
    def page(self, page, **opt):
        return super(CachedWebsite, self).page(page, opt)

    #~ @http.route(['/robots.txt'], type='http', auth="public")
    @memcached.route(flush_type='page_meta')
    def robots(self):
        return super(CachedWebsite, self).robots()

    #~ @http.route('/sitemap.xml', type='http', auth="public", website=True)
    @memcached.route(flush_type='page_meta')
    def sitemap_xml_index(self):
        return super(CachedWebsite, self).sitemap_xml_index()

    #~ @http.route('/website/info', type='http', auth="public", website=True)
    @memcached.route(flush_type='page_meta')
    def website_info(self):
        return super(CachedWebsite, self).website_info()

    #~ @http.route([
        #~ '/website/image',
        #~ '/website/image/<model>/<id>/<field>',
        #~ '/website/image/<model>/<id>/<field>/<int:max_width>x<int:max_height>'
        #~ ], auth="public", website=True, multilang=False)
    @memcached.route(flush_type='page_image')
    def website_image(self, model, id, field, max_width=None, max_height=None):
        return super(CachedWebsite, self).website_image(model, id, field, max_width, max_height)

    #------------------------------------------------------
    # Server actions
    #------------------------------------------------------
    #~ @http.route([
        #~ '/website/action/<path_or_xml_id_or_id>',
        #~ '/website/action/<path_or_xml_id_or_id>/<path:path>',
        #~ ], type='http', auth="public", website=True)
    @memcached.route(flush_type='actions_server')
    def actions_server(self, path_or_xml_id_or_id, **post):
        return super(CachedWebsite, self).actions_server(path_or_xml_id_or_id, **post)
    
    #------------------------------------------------------
    # Flush
    #------------------------------------------------------  
    
    @http.route([
        '/mcflush/page',
    ], type='http', auth="user", website=True)
    def memcached_flush_blog(self,**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='page'),'Flush Page','/mcflush/page'))
     
    @http.route([
        '/mcflush/page/all',
    ], type='http', auth="user", website=True)
    def memcached_flush_blog_all(self,**post):
        memcached.MEMCACHED_CLIENT().delete(memcached.get_keys(flush_type='page'))
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='page'),'Flush Page','/mcflush/page'))
        
    @http.route([
        '/mcflush/page_meta',
    ], type='http', auth="user", website=True)
    def memcached_flush_blog(self,**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='page_meta'),'Flush Page Meta','/mcflush/page_meta'))
     
    @http.route([
        '/mcflush/page_meta/all',
    ], type='http', auth="user", website=True)
    def memcached_flush_blog_all(self,**post):
        memcached.MEMCACHED_CLIENT().delete(memcached.get_keys(flush_type='page_meta'))
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='page_meta'),'Flush Page Meta','/mcflush/page_meta'))
        
    @http.route([
        '/mcflush/page_image',
    ], type='http', auth="user", website=True)
    def memcached_flush_blog(self,**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='page_image'),'Flush Page Image','/mcflush/page_image'))
     
    @http.route([
        '/mcflush/page_image/all',
    ], type='http', auth="user", website=True)
    def memcached_flush_blog_all(self,**post):
        memcached.MEMCACHED_CLIENT().delete(memcached.get_keys(flush_type='page_image'))
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type='page_image'),'Flush Page Image','/mcflush/page_image'))       
    
