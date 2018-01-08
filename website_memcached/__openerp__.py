# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Website MemCached',
    'version': '1.0',
    'category': 'other',
    'summary': 'website acceleration using memcached',
    'description': """
Add mechanisms to cache rendered pages

* Retains existing paths
* Pages with heavy database searches will be extremely fast
* Adds good cach-control for clients and external cach-servers
* Implemented as a easy to use decorator

Each page are given a uniq numeric key hashed from a special raw key.
Default are Database + Path + Context eg {db},{path},{context}

__Url variabels__

path?cache_viewkey      Reports key for a cached path and other meta data and memcached stats
path?cache_invalidate   Removes page from memcached, do not forget to remove it from client cash when you test this.
/mcpage/<key>           View certain page from cache


__Decorator for controller__

Use @memcache.route as drop in replacement for @http.route

    max_age: Number of seconds that the page is permitted in clients cache , default 10 minutes
    cache_age: Number of seconds that the cache will live in memcached, default one day. ETag will be checked every 10 minutes.
    private: True if must not be stored by a shared cache
    key:  function that returns a string that is used as a raw key. The key can use some formats

    Key.format:
        {path}      Url
        {session}   session dict except for session-id
        {context}   context dict except for uid
        {context_uid} context dict with uid
        {uid}       uid
        {logged_in}     user logged in
        {db}        database

    example: key=lambda '{db}{path}%s' % request.website.my_function()

__Example 1 usage for new Controllers:__
from openerp import http
from openerp.addons.website_memcached import memcached
from openerp.addons.web.http import request

class MyController(http.Controller):

    @memcached.route(['/my_path/<string:key>',], type='http', auth="public", website=True, max_age=6000)
    def my_controller(self, key='',**post):
        ...
        return request.website.render("my_template",values) {

__Example 2 usage for adding cache to existing controllers:__
from openerp import http
from openerp.addons.website_memcached import memcached
from openerp.addons.web.http import request
from openerp.addons.website_blog.controllers.main import QueryURL, WebsiteBlog

class CachedBlog(WebsiteBlog):

    @memcached.route(cache_age=3600,key=lambda '{db},{path},{logged_in},%s' % request.website.my_special_function() )
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog,tag,page,**opt)

To install:
    sudo pip install pymemcache
    sudo apt install memcached
""",
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['website','website_blog'],
    'external_dependencies': {'python': ['pymemcache',]},
    'data': [
        'website_view.xml',
],
    'application': False,
}

