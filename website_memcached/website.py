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
import werkzeug

import base64

import logging
_logger = logging.getLogger(__name__)


class MemCachedController(http.Controller):

    @http.route([
        '/mcpage/<string:key>',
    ], type='http', auth="user", website=True)
    def memcached_page(self, key='',**post):
        page_dict = memcached.MEMCACHED_CLIENT().get(key)
        if page_dict:
            return page_dict.get('page').decode('base64')
        return request.registry['ir.http']._handle_exception(None, 404)

    @http.route([
        '/mcpage/<string:key>/delete',
    ], type='http', auth="user", website=True)
    def memcached_page_delete(self, key='',**post):
        page_dict = memcached.MEMCACHED_CLIENT().delete(key)
        if post.get('url'):
            return werkzeug.utils.redirect(post.get('url'), 302)
        return http.Response('<h1>Key is deleted %s</h1>' % (key))

    @http.route([
        '/mcflush',
        '/mcflush/<string:flush_type>',
    ], type='http', auth="user", website=True)
    def memcached_flush(self, flush_type='all',**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type=flush_type), 'Cached Pages %s' % flush_type, '/mcflush/%s' % flush_type, '/mcflush/%s/delete' % flush_type))

    @http.route([
        '/mcflush/<string:flush_type>/delete',
    ], type='http', auth="user", website=True)
    def memcached_flush_delete(self, flush_type='all',**post):
        for key in memcached.get_keys(flush_type=flush_type):
            memcached.MEMCACHED_CLIENT().delete(key)
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type=flush_type), 'Cached Pages %s' % flush_type, '/mcflush/%s' % flush_type, '/mcflush/%s/delete' % flush_type))

    @http.route([
        '/mcmodule',
        '/mcmodule/<string:module>',
    ], type='http', auth="user", website=True)
    def memcached_module(self, module='all',**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(module=module), 'Cached Pages Model %s' % module, '/mcmodule/%s' % module, '/mcmodule/%s/delete' % module))

    @http.route([
        '/mcmodule/<string:module>/delete',
    ], type='http', auth="user", website=True)
    def memcached_module_delete(self, module='all',**post):
        for key in memcached.get_keys(module=module):
            memcached.MEMCACHED_CLIENT().delete(key)
        return http.Response(memcached.get_flush_page(memcached.get_keys(module=module), 'Cached Pages Model %s ' % module, '/mcmodule/%s' % module, '/mcmodule/%s/delete' % module))

    @http.route([
        '/mcpath',
    ], type='http', auth="user", website=True)
    # Example: /mcpath?path=/foo/bar
    def memcached_path(self, path='all',**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(path=path), 'Cached Pages Path %s' % path, '/mcpath?path=%s' % path, '/mcpath/delete?path=%s' % path))

    @http.route([
        '/mcpath/delete',
    ], type='http', auth="user", website=True)
    # Example: /mcpath/delete?path=/foo/bar
    def memcached_path_delete(self, path='all',**post):
        for key in memcached.get_keys(path=path):
            memcached.MEMCACHED_CLIENT().delete(key)
        return http.Response(memcached.get_flush_page(memcached.get_keys(path=path), 'Cached Pages Path %s ' % path, '/mcpath/%s' % path, '/mcpath/delete?path=%s' % path))
