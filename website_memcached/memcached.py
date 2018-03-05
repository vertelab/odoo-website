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
from openerp.service import common
import openerp
import base64
import math
import sys
import traceback

import werkzeug.utils
from werkzeug.http import http_date
from werkzeug import url_encode
import werkzeug

import functools
from timeit import default_timer as timer

import logging
_logger = logging.getLogger(__name__)


import werkzeug.routing

#TODO blacklist pages / context / sessions that not to be cached, parameter on decorator


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
    from pymemcache.client.base import PooledClient,Client,MemcacheClientError,MemcacheUnknownCommandError,MemcacheIllegalInputError,MemcacheServerError,MemcacheUnknownError,MemcacheUnexpectedCloseError
    #~ from pymemcache.client.hash import HashClient
    MEMCACHED__CLIENT__ = False
    MEMCACHED_SERVER = False
    MEMCACHE_CONNECT_TIMEOUT = 10
    MEMCACHE_TIMEOUT = 1
    MEMCACHE_NODELAY = True
    MEMCACHED_VERSION = ''
    #~ MEMCACHED_CLIENT = Client(('localhost', 11211), serializer=serialize_pickle, deserializer=deserialize_pickle)
    #~ from pymemcache.client.murmur3 import murmur3_32 as MEMCACHED_HASH
except Exception as e:
    _logger.info('website_memcached requires pymemcache (pip install pymemcache) %s.' % e)

flush_types = {}

try:
    from pyhashxx import hashxx as MEMCACHED_HASH
except Exception as e:
    _logger.info('missing pyhashxx %s' % e)
def MEMCACHED_CLIENT():
    global MEMCACHED__CLIENT__
    global MEMCACHED_SERVER
    global MEMCACHED_VERSION
    global flush_types
    if not MEMCACHED_SERVER:
        MEMCACHED_SERVER = eval(request.env['ir.config_parameter'].get_param('website_memcached.memcached_db') or '("localhost",11211)')
    if not MEMCACHED__CLIENT__:
        try:
            #~ if type(servers) == list:
                #~ MEMCACHED__CLIENT__ = HashClient(servers, serializer=serialize_pickle, deserializer=deserialize_pickle)
            #~ else:
            MEMCACHED__CLIENT__ = PooledClient(MEMCACHED_SERVER, serializer=serialize_pickle, deserializer=deserialize_pickle,no_delay=MEMCACHE_NODELAY,connect_timeout=MEMCACHE_CONNECT_TIMEOUT,timeout=MEMCACHE_TIMEOUT)
            MEMCACHED_VERSION = MEMCACHED__CLIENT__.version()

            items = MEMCACHED__CLIENT__.stats('items')
            slab_limit = {k.split(':')[1]:v for k,v in MEMCACHED__CLIENT__.stats('items').items() if k.split(':')[2] == 'number' }
            key_lists = [MEMCACHED__CLIENT__.stats('cachedump',slab,str(limit)) for slab,limit in slab_limit.items()]
            keys =  [key for sublist in key_lists for key in sublist.keys()]
            for key in keys:
                page = MEMCACHED__CLIENT__.get(key)
                if page and page.get('db'):
                    if not flush_types.get(page['db'], None):
                        flush_types[page['db']] = set()
                    flush_types[page['db']].add(page.get('flush_type'))

          #~ server: tuple(hostname, port)
          #~ serializer: optional function, see notes in the class docs.
          #~ deserializer: optional function, see notes in the class docs.
          #~ connect_timeout: optional float, seconds to wait for a connection to
            #~ the memcached server. Defaults to "forever" (uses the underlying
            #~ default socket timeout, which can be very long).
          #~ timeout: optional float, seconds to wait for send or recv calls on
            #~ the socket connected to memcached. Defaults to "forever" (uses the
            #~ underlying default socket timeout, which can be very long).
          #~ no_delay: optional bool, set the TCP_NODELAY flag, which may help
            #~ with performance in some cases. Defaults to False.
          #~ ignore_exc: optional bool, True to cause the "get", "gets",
            #~ "get_many" and "gets_many" calls to treat any errors as cache
            #~ misses. Defaults to False.
          #~ socket_module: socket module to use, e.g. gevent.socket. Defaults to
            #~ the standard library's socket module.
          #~ key_prefix: Prefix of key. You can use this as namespace. Defaults
            #~ to b''.
          #~ default_noreply: bool, the default value for 'noreply' as passed to
            #~ store commands (except from cas, incr, and decr, which default to
            #~ False).
          #~ allow_unicode_keys: bool, support unicode (utf8) keys

          #http://pymemcache.readthedocs.io/en/latest/getting_started.html

        except Exception as e:
            err = sys.exc_info()
            error = ''.join(traceback.format_exception(err[0], err[1], err[2]))
            _logger.info('Cannot instantiate MEMCACHED CLIENT\n%s' % error)
            raise MemcacheServerError(e)
        except TypeError as e:
            _logger.info('Type error MEMCACHED CLIENT %s.' % e)
            raise MemcacheServerError(e)

    return MEMCACHED__CLIENT__

# https://lzone.de/cheat-sheet/memcached

def add_flush_type(db, name):
    if flush_types.get(db):
        flush_types[db].add(name)
    else:
        flush_types[db] = set(name)

class website(models.Model):
    _inherit = 'website'

    @api.model
    def flush_types(self):
        if not any(flush_types):
            flush_types[self.env.cr.dbname] = set()
        return flush_types[self.env.cr.dbname]

    @api.model
    def memcache_get(self,key):
        return MEMCACHED_CLIENT().get(MEMCACHED_HASH(key))

    @api.model
    def memcache_set(self,key,value):
        return MEMCACHED_CLIENT().set(MEMCACHED_HASH(key),value)

    @api.model
    def memcache_page(self,key):
        rendered_page = MEMCACHED_CLIENT().get(key)
        if not rendered_page:
            pass
        return rendered_page

    @api.model
    def memcache_flush_types(self):
        return list(flush_types[self.env.cr.dbname])

def get_keys(flush_type=None,module=None,path=None):
    items = MEMCACHED_CLIENT().stats('items')
    slab_limit = {k.split(':')[1]:v for k,v in MEMCACHED_CLIENT().stats('items').items() if k.split(':')[2] == 'number' }
    key_lists = [MEMCACHED_CLIENT().stats('cachedump',slab,str(limit)) for slab,limit in slab_limit.items()]
    keys =  [key for sublist in key_lists for key in sublist.keys()]
    #~ _logger.warn('KEYS: %s' %keys)
    #~ _logger.warn('LEN: %s' %len(keys))

    if flush_type:
       keys = [key for key in keys if flush_type == 'all' or flush_type == mc_load(key).get('flush_type')]
    if module:
       keys = [key for key in keys if module == 'all' or module == mc_load(key).get('module')]
    if path:
       keys = [key for key in keys if path == 'all' or path == mc_load(key).get('path')]
    # Remove other databases
    keys = [key for key in keys if request.env.cr.dbname == mc_load(key).get('db')]

    return keys

def get_flush_page(keys, title, url='', delete_url=''):
    #~ html = '%s<H1>%s</H1><table style="width: 100%%;"><tr><th>Key</th><th>Path</th><th>Module</th><th>Flush_type</th><th>Key Raw</th><th>Cmd</th></tr>' % (('<a href="%s" style="float: right;">delete all</a>' % delete_url) if delete_url else '', title)
    #~ for key in keys:
        #~ p = mc_load(key)
        #~ html += '<tr><td><a href="/mcmeta/%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href="/mcpage/%s/delete?url=%s">delete</a></td></tr>' % (key,key,p.get('path'),p.get('module'),p.get('flush_type'),p.get('key_raw'),key,url)
    #~ html + '</table>'
    rows = []
    for key in keys:
        p = mc_load(key)
        rows.append((
            '<a href="/mcmeta/%s">%s</a>' %(key, key),
            '<a href="%s">%s</a>' %(p.get('path'), p.get('path')),
            p.get('module').replace('openerp.addons.','').split('.')[0],
            p.get('flush_type'),
            p.get('key_raw'),
            '<a href="/mcpage/%s/delete?url=%s" class="fa fa-trash-o"/>' %(key,url)
        ))
    return request.website.render("website_memcached.memcached_page", {
        'title': title,
        'header': [_('Key'),_('Path'),_('Module'),_('Flush Type'),_('Key Raw'),_('Cmd')],
        'rows': rows,
        'delete_url': delete_url,
        'url': url,
        })


    #~ return '<H1>%s</H1><table>%s</table>' % (title,
        #~ ''.join(['<tr><td><a href="/mcpage/%s/delete">%s (delete)</a></td><td></td><td></td></tr>' % (k,k,p.get('path'),p.get('module'),p.get('flush_type')) for key in keys for p,k in [memcached.MEMCACHED_CLIENT().get(key),key]])
def mc_save(key, page_dict,cache_age):
    MEMCACHED_CLIENT().set(key,page_dict,cache_age)
    #~ chunks = [page_dict['page'][i:1000*900] for i in range(int(math.ceil(len(page_dict['page']) / (1000.0*900))))]
    #~ for i,chunk in enumerate(chunks):
        #~ if i == 0:
            #~ page_dict['page'] = chunk
            #~ MEMCACHED_CLIENT().set(key,page_dict,cache_age)
        #~ else:
            #~ MEMCACHED_CLIENT().set('%s-c%d' % (key,i),chunk,cache_age)

def mc_load(key):
    #~ global MEMCACHED_VERSION
    #~ global MEMCACHED_SERVER
    #~ c = Client(MEMCACHED_SERVER or eval(request.env['ir.config_parameter'].get_param('website_memcached.memcached_db') or '("localhost",11211)'), serializer=serialize_pickle, deserializer=deserialize_pickle,no_delay=True,connect_timeout=10,timeout=0.01)
    #~ if not MEMCACHED_VERSION:
        #~ MEMCACHED_VERSION = c.version()
    #~ page_dict = c.get(key)
    #~ c.quit()
    #~ page_dict = MEMCACHED_CLIENT().get(key)
    #~ if type(page_dict) != type({}):
        #~ return {}
    #~ i = 1
    #~ while True:
        #~ chunk = MEMCACHED_CLIENT().get('%s-c%d' % (key,i))
        #~ if not chunk or i > 10:
            #~ break
        #~ page_dict['page'] += chunk
        #~ i += 1
    return MEMCACHED_CLIENT().get(key) or {}

def mc_delete(key):
    MEMCACHED_CLIENT().delete(key)
    #~ i = 1
    #~ while True:
        #~ if not MEMCACHED_CLIENT().delete('%s-c%d' % (key,i)) or i > 10:
            #~ break
        #~ i += 1


def mc_meta(key):
    page_dict = mc_load(key)
    chunks = [page_dict.get('page','') if page_dict else '']
    #~ i = 1
    #~ while True:
        #~ chunk = memcached.MEMCACHED_CLIENT().get('%s-c%d' % (key,i))
        #~ if not chunk or i > 10:
            #~ break
        #~ chunks.append(chunk)
        #~ i += 1
    return {'page_dict':page_dict,'size':len(page_dict.get('page','')) / 1024,'chunks':chunks}

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

    :param max_age: Number of seconds that the page is permitted in clients cache , default 10 minutes
    :param cache_age: Number of seconds that the cache will live in memcached, default one day. ETag will be checked every 10 minutes.
    :param private: True if must not be stored by a shared cache
    :param key:     function that returns a string that is used as a raw key. The key can use some formats {db} {context} {uid} {logged_in}
    :param binary:  do not render page
    :param no_store:  do not store in cache
    :param immutable:  Indicates that the response body will not change over time. The resource, if unexpired, is unchanged on the server and therefore the client should not send a conditional revalidation.  immutable is only honored on https:// transactions
    :param no_transform: No transformations or conversions should be made to the resource (for example do not transform png to jpeg)
    :param s_maxage:  Overrides max-age, but it only applies to shared caches / proxies and is ignored by a private cache
    :param content_type: set Content-Type

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
            #~ _logger.warn('\n\npath: %s\n' % request.httprequest.path)
            if routing.get('key'): # Function that returns a raw string for key making
                # Format {path}{session}{etc}
                key_raw = routing['key'](kw).format(path=request.httprequest.path,
                                                    session='%s' % {k:v for k,v in request.session.items() if len(k)<40},
                                                    device_type='%s' % request.session.get('device_type','md'),  # xs sm md lg
                                                    context='%s' % {k:v for k,v in request.env.context.items() if not k == 'uid'},
                                                    context_uid='%s' % {k:v for k,v in request.env.context.items()},
                                                    uid=request.env.context.get('uid'),
                                                    logged_in='1' if request.env.context.get('uid') > 0 else '0',
                                                    db=request.env.cr.dbname,
                                                    lang=request.env.context.get('lang'),
                                                    post='%s' % kw,
                                                    xmlid='%s' % kw.get('xmlid'),
                                                    version='%s' % kw.get('version'),
                                                    publisher='1' if request.env.ref('base.group_website_publisher') in request.env.user.groups_id else '0',
                                                    designer='1' if request.env.ref('base.group_website_designer') in request.env.user.groups_id else '0',
                                                    ).encode('latin-1')
                #~ raise Warning(request.env['res.users'].browse(request.uid).group_ids)
                key = str(MEMCACHED_HASH(key_raw))
            else:
                key_raw = ('%s,%s,%s' % (request.env.cr.dbname,request.httprequest.path,request.env.context)).encode('latin-1') # Default key
                key = str(MEMCACHED_HASH(key_raw))

############### Key is ready

            if 'cache_invalidate' in kw.keys():
                kw.pop('cache_invalidate',None)
                mc_delete(key)


            page_dict = None
            error = None
            try:
                page_dict = mc_load(key)
            except MemcacheClientError as e:
                error = "MemcacheClientError %s " % e
                _logger.warn(error)
            except MemcacheUnknownCommandError as e:
                error = "MemcacheUnknownCommandError %s " % e
                _logger.warn(error)
            except MemcacheIllegalInputError as e:
                error = "MemcacheIllegalInputError %s " % e
                _logger.warn(error)
            except MemcacheServerError as e:
                error = "MemcacheServerError %s " % e
                _logger.warn(error)
            except MemcacheUnknownError as e:
                error = "MemcacheUnknownError %s key: %s path: %s" % (e,key,request.httprequest.path)
                _logger.warn(error)
                return werkzeug.wrappers.Response(status=500,headers=[
                        ('X-CacheKey',key),
                        ('X-CacheError','MemcacheUnknownError %s' %e),
                        ('X-CacheKeyRaw',key_raw),
                        ('Server','Odoo %s Memcached %s' % (common.exp_version().get('server_version'), MEMCACHED_VERSION)),
                        ])
            except MemcacheUnexpectedCloseError as e:
                error = "MemcacheUnexpectedCloseError %s " % e
                _logger.warn(error)
            except Exception as e:
                err = sys.exc_info()
                error = "Memcached Error %s key: %s path: %s %s" % (e,key,request.httprequest.path, ''.join(traceback.format_exception(err[0], err[1], err[2])))
                _logger.warn(error)
                return werkzeug.wrappers.Response(status=500,headers=[
                        ('X-CacheKey',key),
                        ('X-CacheError','Memcached Error %s' % e),
                        ('X-CacheKeyRaw',key_raw),
                        ('Server','Odoo %s Memcached %s' % (common.exp_version().get('server_version'), MEMCACHED_VERSION)),
                        ])



            if page_dict and not page_dict.get('db') == request.env.cr.dbname:
                _logger.warn('Database violation key=%s stored for=%s  env db=%s ' % (key,page_dict.get('db'),request.env.cr.dbname))
                page_dict = None

            # Blacklist
            if page_dict and any([p if p in request.httprequest.path else '' for p in kw.get('blacklist','').split(',')]):
                page_dict = None

            if 'cache_viewkey' in kw.keys():
                if page_dict:
                    res = mc_meta(key)
                    view_meta = '<h2>Metadata</h2><table>%s</table>' % ''.join(['<tr><td>%s</td><td>%s</td></tr>' % (k,v) for k,v in res['page_dict'].items() if not k == 'page'])
                    view_meta += 'Page Len : %.2f Kb<br>'  % res['size']
                    #~ view_meta += 'Chunks   : %s<br>' % ', '.join([len(c) for c in res['chunks']])
                    view_meta += 'Chunks   : %s<br>' % res['chunks']
                    return http.Response('<h1>Key <a href="/mcpage/%s">%s</a></h1>%s' % (key,key,view_meta))
                else:
                    if error:
                        error = '<h1>Error</h1><h2>%s</h2>' % error
                    return http.Response('%s<h1>Key is missing %s</h1>' % (error if error else '',key))

            if routing.get('add_key') and not 'cache_key' in kw.keys():
                #~ raise Warning(args,kw,request.httprequest.args.copy())
                args = request.httprequest.args.copy()
                args['cache_key'] = key
                return werkzeug.utils.redirect('{}?{}'.format(request.httprequest.path, url_encode(args)), 302)




            max_age = routing.get('max_age',600)              # 10 minutes
            cache_age = routing.get('cache_age',24 * 60 * 60) # One day
            s_maxage =  routing.get('s_maxage',max_age)
            page = None

            if not page_dict:
                _logger.warn('\n\nNo page_dict\n%s\n' % error)
                page_dict = {}
                controller_start = timer()
                response = f(*args, **kw) # calls original controller
                render_start = timer()

                if routing.get('content_type'):
                    response.headers['Content-Type'] = routing.get('content_type')
                    #~ if isinstance(response.headers,list) and isinstance(response.headers[0],tuple):
                        #~ _logger.error('response is list and tuple')
                    #~ header_dict = {h[0]: h[1] for h in response.headers}
                    #~ header_dict['Content-Type'] = routing.get('content_type')
                    #~ response.headers = [(h[0],h[1]) for h in header_dict.items()]

                if not routing.get('binary'):
                    page = response.render()
                else:
                    page = ''.join(response.response)
                page_dict = {
                    'ETag':     '%s' % MEMCACHED_HASH(page),
                    'max-age':  max_age,
                    'cache-age':cache_age,
                    'private':  routing.get('private',False),
                    'key_raw':  key_raw,
                    'render_time': '%.3f sec' % (timer()-render_start),
                    'controller_time': '%.3f sec' % (render_start-controller_start),
                    'path':     request.httprequest.path,
                    'db':       request.env.cr.dbname,
                    'page':     base64.b64encode(page),
                    'date':     http_date(),
                    'module':   f.__module__,
                    'flush_type': routing['flush_type'](kw) if routing.get('flush_type', None) else "",
                    'headers': response.headers,
                    }
                mc_save(key, page_dict,cache_age)
                if routing.get('flush_type'):
                    add_flush_type(request.cr.dbname, routing['flush_type'](kw))
                #~ raise Warning(f.__module__,f.__name__,route())
            else:
                request_dict = {h[0]: h[1] for h in request.httprequest.headers}
                #~ _logger.warn('Page Exists If-None-Match %s Etag %s' %(request_dict.get('If-None-Match'), page_dict.get('ETag')))
                if request_dict.get('If-None-Match') and (request_dict.get('If-None-Match') == page_dict.get('ETag')):
                    #~ _logger.warn('returns 304')
                    return werkzeug.wrappers.Response(status=304,headers=[
                        ('X-CacheETag', page_dict.get('ETag')),
                        ('X-CacheKey',key),
                        ('X-Cache','newly rendered' if page else 'from cache'),
                        ('X-CacheKeyRaw',key_raw),
                        ('X-CacheController',page_dict.get('controller_time')),
                        ('X-CacheRender',page_dict.get('render_time')),
                        ('X-CacheCacheAge',cache_age),
                        ('Server','Odoo %s Memcached %s' % (common.exp_version().get('server_version'), MEMCACHED_VERSION)),
                        ])
            response = http.Response(base64.b64decode(page_dict.get('page'))) # always create a new response (drop response from controller)

            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching
            # https://jakearchibald.com/2016/caching-best-practices/
            #~ if page_dict.get('headers') and isinstance(page_dict['headers'],dict):
                #~ _logger.error('respnse headers dict')
                #~ for k,v in page_dict['headers'].items():
                    #~ response.headers.add(k,v)
                   #response.headers[k] = v
            #~ if page_dict.get('headers') and isinstance(page_dict['headers'],list):
                #~ _logger.error('respnse headers list')

                #~ response.headers = {h[0]: h[1] for h in response.headers}
            if page_dict.get('headers'):
                for k,v in page_dict['headers'].items():
                    #~ response.headers.add(k,v)
                    response.headers[k] = v
            response.headers['Cache-Control'] ='max-age=%s,s-maxage=%s, %s' % (max_age,s_maxage,','.join([keyword for keyword in [routing.get('private','public'),routing.get('no-store'),routing.get('immutable'),routing.get('no-transform'),'no-cache','must-revalidate','proxy-revalidate'] if keyword] )) # private: must not be stored by a shared cache.
            response.headers['ETag'] = page_dict.get('ETag')
            response.headers['X-CacheKey'] = key
            response.headers['X-Cache'] = 'newly rendered' if page else 'from cache'
            response.headers['X-CacheKeyRaw'] = key_raw
            response.headers['X-CacheController'] = page_dict.get('controller_time')
            response.headers['X-CacheRender'] = page_dict.get('render_time')
            response.headers['X-CacheCacheAge'] = cache_age
            response.headers['X-CacheBlacklist'] = kw.get('blacklist','')
            response.headers['Date'] = page_dict.get('date',http_date())
            response.headers['Server'] = 'Odoo %s Memcached %s' % (common.exp_version().get('server_version'), MEMCACHED_VERSION)
            return response

        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    return decorator
