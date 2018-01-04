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
from openerp.http import request
import werkzeug.utils

import functools


import logging
_logger = logging.getLogger(__name__)


#TODO: save ETag, max-age, private, raw key with rendered page, view on cache_viewkey
#TODO save render time on page
#TODO blacklist pages / context / sessions that not to be cached, parameter on decorator
#TODO website_memcached_[blog,crm,sale,event]
#TODO Add database on key or uniqe memcache per database?
#TODO Config of memcache database
#TODO Test: To invalidate cache on local client / cache-server; recreate cache with a new ETag

try:
    import cPickle as pickle
except ImportError:
    import pickle
    
def serialize_pickle(key, value):
    if isinstance(value, str):
        return value, 1
    return pickle.dumps(value), 2

def deserialize_pickle(key, value, flags):
    if flags == 1:
        return value
    if flags == 2:
        return pickle.loads(value)
    raise Exception('Unknown flags for value: {1}'.format(flags))  
    
try:
    from pymemcache.client.base import Client
    MEMCACHED_CLIENT = Client(('localhost', 11211), serializer=serialize_pickle, deserializer=deserialize_pickle)
    from pymemcache.client.murmur3 import murmur3_32 as MEMCACHED_HASH
except Exception as e:
    _logger.info('website_memcached requires pymemcache (pip install pymemcache) %s.' % e)

# https://lzone.de/cheat-sheet/memcached

class website(models.Model):
    _inherit = 'website'

    @api.model
    def memcache_get(self,key):
        return MEMCACHED_CLIENT.get(MEMCACHED_HASH(key))

    @api.model
    def memcache_set(self,key,value):
        return MEMCACHED_CLIENT.set(MEMCACHED_HASH(key),value)

    @api.model
    def memcache_page(self,key):
        rendered_page = MEMCACHED_CLIENT.get(key)
        if not rendered_page:
            pass
        return rendered_page


def route(route=None, **kw):
    """
    Decorator marking the decorated method as being a handler for
    requests. The method must be part of a subclass of ``Controller``.

    memcached.route instead of http.route

    :param route: string or array. The route part that will determine which
                  http requests will match the decorated method. Can be a
                  single string or an array of strings. See werkzeug's routing
                  documentation for the format of route expression (
                  http://werkzeug.pocoo.org/docs/routing/ ).
    :param type: The type of request, can be ``'http'`` or ``'json'``.
    :param auth: The type of authentication method, can on of the following:

                 * ``user``: The user must be authenticated and the current request
                   will perform using the rights of the user.
                 * ``public``: The user may or may not be authenticated. If she isn't,
                   the current request will perform using the shared Public user.
                 * ``none``: The method is always active, even if there is no
                   database. Mainly used by the framework and authentication
                   modules. There request code will not have any facilities to access
                   the database nor have any configuration indicating the current
                   database nor the current user.
    :param methods: A sequence of http methods this route applies to. If not
                    specified, all methods are allowed.
    :param cors: The Access-Control-Allow-Origin cors directive value.

---- Cache specific params

    :param max-age: Number of seconds that the cache will live, default one day
    :param private: True if must not be stored by a shared cache
    :param key:  function that returns a string that is used as a raw key. The key can use some formats {context} {uid} {logged_in}
    : 
    """
    routing = kw.copy()
    assert not 'type' in routing or routing['type'] in ("http", "json")
    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing['routes'] = routes
        @functools.wraps(f)
        def response_wrap(*args, **kw):
            if routing.get('key'): # Function that returns a raw string for key making
                # Format {path}{session}{etc}
                key_raw = routing['key']().format(  path=request.httprequest.path,
                                                    session={k:v for k,v in request.session.items() if len(k)<40},
                                                    context={k:v for k,v in request.env.context.items() if not k == 'uid'},
                                                    uid=request.env.context.get('uid'),
                                                    logged_in='1' if request.env.context.get('uid') > 0 else '0',
                                                    )
                key = str(MEMCACHED_HASH(key_raw))
            else:
                key = str(MEMCACHED_HASH('%s,%s' %(request.httprequest.path,request.env.context)))

            if routing.get('max-age'):
                max_age = routing['max-age']
            else:
                max_age = 24 * 60 * 60  # One day

            if 'cache_invalidate' in kw.keys():
                MEMCACHED_CLIENT.delete(key)
            if 'cache_viewkey' in kw.keys():
                return http.Response('<h1>Key <a href="/mcpage/%s">%s</a></h1>%s' % 
                    (key,key,'<table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (key,value) for key,value in MEMCACHED_CLIENT.stats().items()])) +
                    '%s' % MEMCACHED_CLIENT.stats('items'))

            page = MEMCACHED_CLIENT.get(key)
            
            if not page:
                response = f(*args, **kw)
                page = response.render()
                MEMCACHED_CLIENT.set(key,page,max_age)
            else:
                response = http.Response(page)
                
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching
            response.headers['Cache-Control'] ='max-age=%s, %s' % (max_age,'private' if routing.get('private') else 'public') # private: must not be stored by a shared cache.
            response.headers['ETag'] = MEMCACHED_HASH(page)
            return response

        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    return decorator
