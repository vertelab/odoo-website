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

    @http.route(['/mcpage/<string:key>',], type='http', auth="user", website=True)
    def memcached_page(self, key='',**post):
        _logger.warn('Herw I am')
        page_dict = memcached.mc_load(key)
        if page_dict:
            return page_dict.get('page').decode('base64')
        return request.registry['ir.http']._handle_exception(None, 404)

    @http.route(['/mcpage/<string:key>/delete',], type='http', auth="user", website=True)
    def memcached_page_delete(self, key='',**post):
        memcached.mc_delete(key)
        if post.get('url'):
            return werkzeug.utils.redirect(post.get('url'), 302)
        return http.Response('<h1>Key is deleted %s</h1>' % (key))

    @http.route(['/mcmeta/<string:key>',], type='http', auth="user", website=True)
    def memcached_meta(self, key='',**post):
        res = memcached.mc_meta(key)
        view_meta = '<h2>Metadata</h2><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in res['page_dict'].items() if not k == 'page'])
        view_meta += 'Page Len : %.2f Kb<br>'  % res['size']
        view_meta += 'Chunks   : %s<br>' % ', '.join([len(c) for c in res['chunks']])
        return http.Response('<h1>Key <a href="/mcpage/%s">%s</a></h1>%s' % (key,key,view_meta))

    @http.route(['/mcflush','/mcflush/<string:flush_type>',], type='http', auth="user", website=True)
    def memcached_flush(self, flush_type='all',**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type=flush_type), 'Cached Pages %s' % flush_type, '/mcflush/%s' % flush_type, '/mcflush/%s/delete' % flush_type))

    @http.route(['/mcflush/<string:flush_type>/delete',], type='http', auth="user", website=True)
    def memcached_flush_delete(self, flush_type='all',**post):
        for key in memcached.get_keys(flush_type=flush_type):
            memcached.mc_delete(key)
        return http.Response(memcached.get_flush_page(memcached.get_keys(flush_type=flush_type), 'Cached Pages %s' % flush_type, '/mcflush/%s' % flush_type, '/mcflush/%s/delete' % flush_type))

    @http.route(['/mcmodule','/mcmodule/<string:module>',], type='http', auth="user", website=True)
    def memcached_module(self, module='all',**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(module=module), 'Cached Pages Model %s' % module, '/mcmodule/%s' % module, '/mcmodule/%s/delete' % module))

    @http.route(['/mcmodule/<string:module>/delete',], type='http', auth="user", website=True)
    def memcached_module_delete(self, module='all',**post):
        for key in memcached.get_keys(module=module):
            memcached.mc_delete(key)
        return http.Response(memcached.get_flush_page(memcached.get_keys(module=module), 'Cached Pages Model %s ' % module, '/mcmodule/%s' % module, '/mcmodule/%s/delete' % module))

    @http.route(['/mcpath',], type='http', auth="user", website=True)
    # Example: /mcpath?path=/foo/bar
    def memcached_path(self, path='all',**post):
        return http.Response(memcached.get_flush_page(memcached.get_keys(path=path), 'Cached Pages Path %s' % path, '/mcpath?path=%s' % path, '/mcpath/delete?path=%s' % path))

    @http.route(['/mcpath/delete',], type='http', auth="user", website=True)
    # Example: /mcpath/delete?path=/foo/bar
    def memcached_path_delete(self, path='all',**post):
        for key in memcached.get_keys(path=path):
            memcached.mc_delete(key)
        return http.Response(memcached.get_flush_page(memcached.get_keys(path=path), 'Cached Pages Path %s ' % path, '/mcpath/%s' % path, '/mcpath/delete?path=%s' % path))

    @http.route(['/mcstats',], type='http', auth="user", website=True)
    def memcached_stats(self, **post):
        slab_limit = {k.split(':')[1]:v for k,v in memcached.MEMCACHED_CLIENT().stats('items').items() if k.split(':')[2] == 'number' }
        key_lists = [memcached.MEMCACHED_CLIENT().stats('cachedump',slab,str(limit)) for slab,limit in slab_limit.items()]
        return http.Response(
        '<h1>Memcached Stat</h1><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in memcached.MEMCACHED_CLIENT().stats().items()]) +
        '<h2>Items</h2><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in memcached.MEMCACHED_CLIENT().stats('items').items()]) +
        '<h2>Slab Limit</h2>%s' % slab_limit +
        '<h2>Key Lists</h2>%s' % key_lists +
        '<h2>Keys</h2>%s' % [key for sublist in key_lists for key in sublist.keys()])

        #~ view_stat = '<h1>Memcached Stat</h1><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in MEMCACHED_CLIENT().stats().items()])
        #~ view_items = '<h2>Items</h2><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in MEMCACHED_CLIENT().stats('items').items()])
