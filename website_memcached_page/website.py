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

import openerp
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website.controllers.main import Website

from openerp import models, fields, api, _


import logging
_logger = logging.getLogger(__name__)

    
class CachedWebsite(Website):

    #~ @http.route('/page/<page:page>', type='http', auth="public", website=True)
    @memcached.route(flush_type='page')
    def page(self, page, **opt):
        return super(CachedWebsite, self).page(page, **opt)

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
    @memcached.route(flush_type='page_image',binary=True)
    def website_image(self, model, id, field, max_width=None, max_height=None):
        raise Warning(model,id,field)
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
    

    #------------------------------------------------------
    # from web
    #------------------------------------------------------
class CachedBinary(openerp.addons.web.controllers.main.Binary):

    #~ @http.route([
        #~ '/web/binary/company_logo',
        #~ '/logo',
        #~ '/logo.png',
    #~ ], type='http', auth="none", cors="*")
    @memcached.route(flush_type='page_image',binary=True)
    def company_logo(self, dbname=None, **kw):
        return super(CachedBinary, self).company_logo(dbname, **kw)
    
#~ class Website(models.Model):
    #~ _inherit = 'website'
        
    #~ def _image(self, cr, uid, model, id, field, response, max_width=maxint, max_height=maxint, cache=None, context=None):
        #~ """ Fetches the requested field and ensures it does not go above
        #~ (max_width, max_height), resizing it if necessary.

        #~ Resizing is bypassed if the object provides a $field_big, which will
        #~ be interpreted as a pre-resized version of the base field.

        #~ If the record is not found or does not have the requested field,
        #~ returns a placeholder image via :meth:`~._image_placeholder`.

        #~ Sets and checks conditional response parameters:
        #~ * :mailheader:`ETag` is always set (and checked)
        #~ * :mailheader:`Last-Modified is set iif the record has a concurrency
          #~ field (``__last_update``)

        #~ The requested field is assumed to be base64-encoded image data in
        #~ all cases.
        #~ """
        #~ Model = self.pool[model]
        #~ id = int(id)

        #~ ids = None
        #~ if Model.check_access_rights(cr, uid, 'read', raise_exception=False):
            #~ ids = Model.search(cr, uid,
                               #~ [('id', '=', id)], context=context)
        #~ if not ids and 'website_published' in Model._fields:
            #~ ids = Model.search(cr, openerp.SUPERUSER_ID,
                               #~ [('id', '=', id), ('website_published', '=', True)], context=context)
        #~ if not ids:
            #~ return self._image_placeholder(response)

        #~ concurrency = '__last_update'
        #~ [record] = Model.read(cr, openerp.SUPERUSER_ID, [id],
                              #~ [concurrency, field],
                              #~ context=context)

        #~ if concurrency in record:
            #~ server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            #~ try:
                #~ response.last_modified = datetime.datetime.strptime(
                    #~ record[concurrency], server_format + '.%f')
            #~ except ValueError:
                #~ # just in case we have a timestamp without microseconds
                #~ response.last_modified = datetime.datetime.strptime(
                    #~ record[concurrency], server_format)

        #~ # Field does not exist on model or field set to False
        #~ if not record.get(field):
            #~ # FIXME: maybe a field which does not exist should be a 404?
            #~ return self._image_placeholder(response)

        #~ response.set_etag(hashlib.sha1(record[field]).hexdigest())
        #~ response.make_conditional(request.httprequest)

        #~ if cache:
            #~ response.cache_control.max_age = cache
            #~ response.expires = int(time.time() + cache)

        #~ # conditional request match
        #~ if response.status_code == 304:
            #~ return response

        #~ data = record[field].decode('base64')
        #~ image = Image.open(cStringIO.StringIO(data))
        #~ response.mimetype = Image.MIME[image.format]

        #~ filename = '%s_%s.%s' % (model.replace('.', '_'), id, str(image.format).lower())
        #~ response.headers['Content-Disposition'] = 'inline; filename="%s"' % filename

        #~ if (not max_width) and (not max_height):
            #~ response.data = data
            #~ return response

        #~ w, h = image.size
        #~ max_w = int(max_width) if max_width else maxint
        #~ max_h = int(max_height) if max_height else maxint

        #~ if w < max_w and h < max_h:
            #~ response.data = data
        #~ else:
            #~ size = (max_w, max_h)
            #~ img = image_resize_and_sharpen(image, size, preserve_aspect_ratio=True)
            #~ image_save_for_web(img, response.stream, format=image.format)
            #~ # invalidate content-length computed by make_conditional as
            #~ # writing to response.stream does not do it (as of werkzeug 0.9.3)
            #~ del response.headers['Content-Length']

        #~ return response
