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

from odoo import http
from odoo.http import request
from odoo.addons.website_memcached import memcached

import werkzeug
import base64

import logging
_logger = logging.getLogger(__name__)

class MemCachedController(http.Controller):
    def memcached_check_group(self, user=None):
        """Check if the logged in user is allowed to administrate the cache."""
        user = user or request.env.user
        if not user.has_group('base.group_website_designer'):
            raise Warning("Only website administrators are allowed to administrate the cache!")

    @http.route(['/mcpage/<string:key>',], type='http', auth="user", website=True)
    def memcached_page(self, key='', **post):
        self.memcached_check_group()
        page_dict = memcached.mc_load(key)
        if page_dict:
            return page_dict.get('page').decode('base64')
        return request.registry['ir.http']._handle_exception(None, 404)

    @http.route(['/mcpage/<string:key>/delete',], type='http', auth="user", website=True)
    def memcached_page_delete(self, key='',**post):
        self.memcached_check_group()
        memcached.mc_delete(key)
        if post.get('url'):
            return werkzeug.utils.redirect(post.get('url'), 302)
        return http.Response('<h1>Key is deleted %s</h1>' % (key))

    @http.route(['/mcmeta/<string:key>',], type='http', auth="user", website=True)
    def memcached_meta(self, key='',**post):
        self.memcached_check_group()
        res = memcached.mc_meta(key)

        values = {
            'url': '/mcpage/%s' %key,
            'key': key,
            'page_dict': res['page_dict'].items(),
            'page_len': '%.2f' %res['size'],
        }
        return request.website.render('website_memcached.mcmeta_page', values)

    @http.route(['/mcflush','/mcflush/<string:flush_type>',], type='http', auth="user", website=True)
    def memcached_flush(self, flush_type='all',**post):
        self.memcached_check_group()
        return memcached.get_flush_page(memcached.get_keys(flush_type=flush_type, load=True), 'Cached Pages %s' % flush_type, '/mcflush/%s' % flush_type, '/mcflush/%s/delete' % flush_type)

    @http.route(['/mcetag','/mcetag/<string:etag>',], type='http', auth="user", website=True)
    def memcached_etag(self, etag='all',**post):
        self.memcached_check_group()
        return memcached.get_flush_page(memcached.get_keys(etag=etag, load=True), 'Cached Pages Etag %s' % etag, '/mcetag/%s' % etag, '/mcetag/%s/delete' % etag)

    @http.route(['/mcflush/<string:flush_type>/delete',], type='http', auth="user", website=True)
    def memcached_flush_delete(self, flush_type='all',**post):
        self.memcached_check_group()
        memcached.mc_delete(memcached.get_keys(flush_type=flush_type))
        return werkzeug.utils.redirect('/mcflush/%s' % flush_type, 302)

    @http.route(['/mcmodule','/mcmodule/<string:module>',], type='http', auth="user", website=True)
    def memcached_module(self, module='all',**post):
        self.memcached_check_group()
        return memcached.get_flush_page(memcached.get_keys(module=module, load=True), 'Cached Pages Model %s' % module, '/mcmodule/%s' % module, '/mcmodule/%s/delete' % module)

    @http.route(['/mcmodule/<string:module>/delete',], type='http', auth="user", website=True)
    def memcached_module_delete(self, module='all',**post):
        self.memcached_check_group()
        memcached.mc_delete(memcached.get_keys(module=module))
        return werkzeug.utils.redirect('/mcmodule/%s' % module, 302)

    @http.route(['/mcpath',], type='http', auth="user", website=True)
    # Example: /mcpath?path=/foo/bar
    def memcached_path(self, path='all',**post):
        self.memcached_check_group()
        return memcached.get_flush_page(memcached.get_keys(path=path, load=True), 'Cached Pages Path %s' % path, '/mcpath?path=%s' % path, '/mcpath/delete?path=%s' % path)

    @http.route(['/mcpath/delete',], type='http', auth="user", website=True)
    # Example: /mcpath/delete?path=/foo/bar
    def memcached_path_delete(self, path='all',**post):
        self.memcached_check_group()
        memcached.mc_delete(memcached.get_keys(path=path))
        return werkzeug.utils.redirect('/mcpath?path=%s' % path, 302)

    @http.route(['/mcflushall',], type='http', auth="user", website=True)
    def memcached_flush_all(self, **post):
        """Flush the entire cache, regardless of keys, databases etc."""
        self.memcached_check_group()
        memcached.mc_flush_all()
        return werkzeug.utils.redirect('/mcflush', 302)

    @http.route(['/mcstatus','/mcstatus/<int:status_code>',], type='http', auth="user", website=True)
    def memcached_status_code(self, status_code='all',**post):
        self.memcached_check_group()
        return memcached.get_flush_page(memcached.get_keys(status_code=status_code, load=True), 'Cached Pages Status %s' % status_code, '/mcstatus/%s' % status_code, '/mcstatus/%s/delete' % status_code)

    @http.route(['/mcstatus/all/delete', '/mcstatus/<int:status_code>/delete',], type='http', auth="user", website=True)
    def memcached_status_code_delete(self, status_code='all',**post):
        self.memcached_check_group()
        memcached.mc_delete(memcached.get_keys(status_code=status_code))
        return werkzeug.utils.redirect('/mcstatus/%s' % status_code, 302)
    
    @http.route(['/mcclearpath',], type='http', auth="user", website=True)
    # Example: /mcpath?path=/foo/bar
    def memcached_clear_path(self, path='all',**post):
        self.memcached_check_group()
        memcached.mc_delete(memcached.get_keys(path=path))
        return request.redirect(path, code=302)

    @http.route(['/mcstats',], type='http', auth="user", website=True)
    def memcached_stats(self, **post):
        self.memcached_check_group()
        slab_limit = {k.split(':')[1]:v for k,v in memcached.MEMCACHED_CLIENT().stats('items').items() if k.split(':')[2] == 'number' }
        key_lists = [memcached.MEMCACHED_CLIENT().stats('cachedump',slab,str(limit)) for slab,limit in slab_limit.items()]
        return http.Response(
        '<h1>Memcached Stat</h1><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in memcached.MEMCACHED_CLIENT().stats().items()]) +
        '<h2>Items</h2><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in memcached.MEMCACHED_CLIENT().stats('items').items()]) +
        '<h2>Slab Limit</h2>%s' % slab_limit +
        '<h2>Key Lists</h2>%s' % key_lists +
        '<h2>Keys</h2>%s' % [key for sublist in key_lists for key in sublist.keys()])

    @http.route(['/memcache/stats',], type='http', auth="user", website=True)
    def memcache_statistics(self, **post):
        self.memcached_check_group()
        slab_stats = request.website.memcache_get_stats('slabs')
        slabs = {}
        for key in slab_stats.keys():
            key_s = key.split(':')
            if len(key_s) > 1:
                value = slab_stats[key]
                key_name = key_s[1]
                slab = int(key_s[0])
                if slab not in slabs:
                    slabs[slab] = {}
                slabs[slab][key_name] = value
                del slab_stats[key]
        slab_stats['slabs'] = slabs
        values = {
            'stats': request.website.memcache_get_stats(),
            'slabs': slab_stats,
            'items': request.website.memcache_get_stats('items'),
            'stats_desc': request.website.memcache_get_stats_desc(),
            'slabs_desc': request.website.memcache_get_stats_desc('slabs'),
            'items_desc': request.website.memcache_get_stats_desc('items'),
            'sorted': sorted,
        }
        return request.website.render('website_memcached.statistics_page', values)
