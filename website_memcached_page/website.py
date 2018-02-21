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
    @memcached.route(flush_type='page', key=lambda k: '{db}{path}{logged_in}{lang}')
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
    @memcached.route(flush_type='page_image',binary=True, key=lambda k: '{db}{path}')
    def website_image(self, model, id, field, max_width=None, max_height=None):
        #~ raise Warning(model,id,field)
        return super(CachedWebsite, self).website_image(model, id, field, max_width, max_height)

    #------------------------------------------------------
    # Server actions
    #------------------------------------------------------
    #~ @http.route([
        #~ '/website/action/<path_or_xml_id_or_id>',
        #~ '/website/action/<path_or_xml_id_or_id>/<path:path>',
        #~ ], type='http', auth="public", website=True)
    #~ @memcached.route(flush_type='actions_server')
    #~ def actions_server(self, path_or_xml_id_or_id, **post):
        #~ return super(CachedWebsite, self).actions_server(path_or_xml_id_or_id, **post)


class CachedBinary(openerp.addons.web.controllers.main.Binary):

    #~ @http.route([
        #~ '/web/binary/company_logo',
        #~ '/logo',
        #~ '/logo.png',
    #~ ], type='http', auth="none", cors="*")
    @memcached.route(flush_type='page_image',binary=True)
    def company_logo(self, dbname=None, **kw):
        return super(CachedBinary, self).company_logo(dbname, **kw)


class CachedHome(openerp.addons.web.controllers.main.Home):

    #~ @http.route([
        #~ '/web/js/<xmlid>',
        #~ '/web/js/<xmlid>/<version>',
    #~ ], type='http', auth='public')
    #~ @memcached.route(flush_type='js_bundle',binary=True,cache_age=60*60*24*30,max_age=604800)
    #~ def js_bundle(self, xmlid, version=None, **kw):
        #~ return super(CachedHome, self).js_bundle(xmlid, version, **kw)
    #~ @http.route([/web/js/website.assets_frontend/6
        #~ '/web/js/<xmlid>',
        #~ '/web/js/<xmlid>/<version>',
    #~ ], type='http', auth='public')
    @memcached.route(['/web/js/website.assets_frontend/<version>',
                      '/web/js/web.assets_common/<version>',
                      '/web/js/website.assets_editor/<version>'],flush_type='js_bundle',binary=True,cache_age=60*60*24*30,max_age=604800)
    def js_bundle_special(self, version=None, **kw):
        if 'website.assets_frontend' in request.httprequest.path:
            return super(CachedHome, self).js_bundle('website.assets_frontend', version, **kw)
        if 'web.assets_common' in request.httprequest.path:
            return super(CachedHome, self).js_bundle('web.assets_common', version, **kw)
        if 'website.assets_editor' in request.httprequest.path:
            return super(CachedHome, self).js_bundle('website.assets_editor', version, **kw)



    #~ @http.route([
        #~ '/web/css/<xmlid>',
        #~ '/web/css/<xmlid>/<version>',
        #~ '/web/css.<int:page>/<xmlid>/<version>',
    #~ ], type='http', auth='public')
    @memcached.route(flush_type='css_bundle',binary=True,cache_age=60*60*24*30,max_age=604800,key=lambda k: '{db}{xmlid}',content_type="text/css; charset=utf-8;")
    #~ @memcached.route(flush_type='css_bundle',binary=True,cache_age=60*60*24*30,max_age=604800,key=lambda k: '{db}{xmlid}')
    def css_bundle(self, xmlid, version=None, page=None, **kw):
        return super(CachedHome, self).css_bundle(xmlid, version, page, **kw)

class MemCachedController(http.Controller):
    @http.route(['/remove_cached_page',], type='json', auth="user", website=True)
    def remove_cached_page(self, url='',**kw):
        for key in memcached.get_keys(flush_type='page', path=url):
            memcached.mc_delete(key)
        return 'deleted'
