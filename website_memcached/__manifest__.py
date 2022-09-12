# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Website: Website MemCached',
    'version': '14.0.1.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Website acceleration using memcached.',
    'category': 'Website',
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-website/website_memcashed',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-website',
    "description": """
Add mechanisms to cache rendered pages

* Retains existing paths
* Pages with heavy database searches will be extremely fast
* Adds good cach-control for clients and external cach-servers
* Implemented as an easy to use decorator and an easy method for enhance existing controllers

Each page are given a uniq numeric key hashed from a special raw key.
Default are Database + Path + Context eg {db},{path},{context}

##Url variabels##

  path?cache_viewkey      Reports key for a cached path and other meta data and memcached stats
  path?cache_invalidate   Removes page from memcached, do not forget to remove it from client cash when you test this.
  /mcpage/<key>           View certain page from cache
  /mcflush/<fluch_key>    Views a list of pages from the cache, flush_key == all: all keys for current database


##Decorator for controller##

 Use @memcache.route as drop in replacement for @http.route

    max_age:   Number of seconds that the page is permitted in clients cache , default 10 minutes
    cache_age: Number of seconds that the cache will live in memcached, default one day. ETag will be checked every 10 minutes.
    private:   True if must not be stored by a shared cache
    key:       Function that returns a string that is used as a raw key. The key can use some formats

    Key.format:
        {path}      Url
        {session}   session dict except for session-id
        {context}   context dict except for uid
        {context_uid} context dict with uid
        {uid}       uid
        {logged_in} user logged in
        {db}        database, this is important! Pages with database violations won't be used

    example: key=lambda '{db}{path}%s' % request.website.my_function()

##Example 1 usage for new Controllers:
 from openerp import http
 from openerp.addons.website_memcached import memcached
 from openerp.addons.web.http import request

 class MyController(http.Controller):

    @memcached.route(['/my_path/<string:key>',], type='http', auth="public", website=True, max_age=6000)
    def my_controller(self, key='',**post):
        ...
        return request.website.render("my_template",values) {

#Example 2 usage for adding cache to existing controllers:__
 from openerp import http
 from openerp.addons.website_memcached import memcached
 from openerp.addons.web.http import request
 from openerp.addons.website_blog.controllers.main import QueryURL, WebsiteBlog

 class CachedBlog(WebsiteBlog):

    @memcached.route(cache_age=3600,key=lambda '{db},{path},{logged_in},%s' % request.website.my_special_function() )
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog,tag,page,**opt)

#To install:
    sudo pip install pymemcache
    sudo apt install memcached

    check /etc/memcached.conf
    Update Memcached config in Website Settings with one or more server tupples; [('server1',<port>),('server2',<port>)]

""",
    "depends": ["website"],
    "external_dependencies": {"python": ["pymemcache", "pyhashxx"]},
    "data": [
        "views/res_config_view.xml",
        "views/website_view.xml",
    ],
    "application": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
