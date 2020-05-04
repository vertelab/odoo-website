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
from time import time

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
    MEMCACHE_TIMEOUT = 5
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
        try:
            MEMCACHED_SERVER = eval(request.env['ir.config_parameter'].get_param('website_memcached.memcached_db') or '("localhost",11211)')
        except:
            MEMCACHED_SERVER = ("localhost",11211)
    if not MEMCACHED__CLIENT__:
        try:
            #~ if type(servers) == list:
                #~ MEMCACHED__CLIENT__ = HashClient(servers, serializer=serialize_pickle, deserializer=deserialize_pickle)
            #~ else:
            MEMCACHED__CLIENT__ = PooledClient(MEMCACHED_SERVER, serializer=serialize_pickle, deserializer=deserialize_pickle,no_delay=MEMCACHE_NODELAY,connect_timeout=MEMCACHE_CONNECT_TIMEOUT,timeout=MEMCACHE_TIMEOUT)
            MEMCACHED_VERSION = MEMCACHED__CLIENT__.version()

       ## Retreive all flush_types per database

            # https://www.tutorialspoint.com/memcached/memcached_stats_items.htm
            # echo "stats items"|nc localhost 11211|grep number
            #    STAT items:11:number 3
            #    STAT items:12:number 3
            #    STAT items:13:number 1
            #    STAT items:14:number 19
            #    STAT items:15:number 1212

            items = MEMCACHED__CLIENT__.stats('items')
            slab_limit = {k.split(':')[1]:v for k,v in MEMCACHED__CLIENT__.stats('items').items() if k.split(':')[2] == 'number' }  # slab -> limit
            
            # echo "stats cachedump 15 1212 "|nc localhost 11211  # slab limit
            # ITEM 4092067750 [2231 b; 1561018218 s]
            # ITEM 3699334878 [1974 b; 1560964179 s]
            # ITEM 2768968127 [2071 b; 1560968016 s]
            # ITEM 2482188247 [2126 b; 1561020033 s]
            # ITEM 2293401784 [2086 b; 1560972986 s]

            key_lists = [MEMCACHED__CLIENT__.stats('cachedump',slab,str(limit)) for slab,limit in slab_limit.items()]  # List of lists
            keys =  [key for sublist in key_lists for key in sublist.keys()]  # [4092067750, 3699334878 ...]             flattended list
            for key in keys:
                page = MEMCACHED__CLIENT__.get(key)
                # echo "get 4092067750 "|nc localhost 11211  -> dict with data
                
                if page and page.get('db'):
                    if not flush_types.get(page['db'], None):
                        flush_types[page['db']] = set()
                    flush_types[page['db']].add(page.get('flush_type'))

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
    if not flush_types.get(db):
        flush_types[db] = set()
    flush_types[db].add(name)

def clean_text(text):
    """Scrub away filthy characters that werkzeug doesn't like to get back in headers."""
    # I remember writing this, but I can't remember why text.encode('latin1', 'replace') didn't work.
    res = ''
    for c in text:
        try:
            c.encode('latin1')
            res += c
        except:
            res += '?'
    return res

class website(models.Model):
    _inherit = 'website'
    
    @api.model
    def flush_types(self):
        db = self.env.cr.dbname
        if db not in flush_types:
            flush_types[db] = set()
        return flush_types[db]
    
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
    
    @api.model
    def memcache_get_stats(self, *args):
        return MEMCACHED_CLIENT().stats(*args)
    
    @api.model
    def memcache_get_stats_desc(self, *args):
        standard = {'bytes': {'data_type': '64u',
                               'description': 'Current number of bytes used by this server to store items.',
                               'version': ''},
                     'bytes_read': {'data_type': '64u',
                                    'description': 'Total number of bytes read by this server from network.',
                                    'version': ''},
                     'bytes_written': {'data_type': '64u',
                                       'description': 'Total number of bytes sent by this server to network.',
                                       'version': ''},
                     'cas_badvalue': {'data_type': '64u',
                                      'description': 'Number of keys that have been compared and swapped, but the comparison (original) value did not match the supplied value.',
                                      'version': '1.3.x'},
                     'cas_hits': {'data_type': '64u',
                                  'description': 'Number of keys that have been compared and swapped and found present.',
                                  'version': '1.3.x'},
                     'cas_misses': {'data_type': '64u',
                                    'description': 'Number of items that have been compared and swapped and not found.',
                                    'version': '1.3.x'},
                     'cmd_get': {'data_type': '64u',
                                 'description': 'Total number of retrieval requests (get operations).',
                                 'version': ''},
                     'cmd_set': {'data_type': '64u',
                                 'description': 'Total number of storage requests (set operations).',
                                 'version': ''},
                     'conn_yields': {'data_type': '64u',
                                     'description': 'Number of yields for connections (related to the -R option).',
                                     'version': '1.4.0'},
                     'connection_structures': {'data_type': '32u',
                                               'description': 'Number of connection structures allocated by the server.',
                                               'version': ''},
                     'curr_connections': {'data_type': '32u',
                                          'description': 'Current number of open connections.',
                                          'version': ''},
                     'curr_items': {'data_type': '32u',
                                    'description': 'Current number of items stored by this instance.',
                                    'version': ''},
                     'decr_hits': {'data_type': '64u',
                                   'description': 'Number of keys that have been decremented and found present.',
                                   'version': '1.3.x'},
                     'decr_misses': {'data_type': '64u',
                                     'description': 'Number of items that have been decremented and not found.',
                                     'version': '1.3.x'},
                     'delete_hits': {'data_type': '64u',
                                     'description': 'Number of keys that have been deleted and found present.',
                                     'version': '1.3.x'},
                     'delete_misses': {'data_type': '64u',
                                       'description': 'Number of items that have been delete and not found.',
                                       'version': '1.3.x'},
                     'evictions': {'data_type': '64u',
                                   'description': 'Number of valid items removed from cache to free memory for new items.',
                                   'version': ''},
                     'get_hits': {'data_type': '64u',
                                  'description': 'Number of keys that have been requested and found present.',
                                  'version': ''},
                     'get_misses': {'data_type': '64u',
                                    'description': 'Number of items that have been requested and not found.',
                                    'version': ''},
                     'incr_hits': {'data_type': '64u',
                                   'description': 'Number of keys that have been incremented and found present.',
                                   'version': '1.3.x'},
                     'incr_misses': {'data_type': '64u',
                                     'description': 'Number of items that have been incremented and not found.',
                                     'version': '1.3.x'},
                     'limit_maxbytes': {'data_type': '32u',
                                        'description': 'Number of bytes this server is permitted to use for storage.',
                                        'version': ''},
                     'pid': {'data_type': '32u',
                             'description': 'Process ID of the memcached instance.',
                             'version': ''},
                     'pointer_size': {'data_type': 'string',
                                      'description': 'Size of pointers for this host specified in bits (32 or 64).',
                                      'version': ''},
                     'rusage_system': {'data_type': '32u:32u',
                                       'description': 'Total system time for this instance (seconds:microseconds).',
                                       'version': ''},
                     'rusage_user': {'data_type': '32u:32u',
                                     'description': 'Total user time for this instance (seconds:microseconds).',
                                     'version': ''},
                     'threads': {'data_type': '32u',
                                 'description': 'Number of worker threads requested.',
                                 'version': ''},
                     'time': {'data_type': '32u',
                              'description': 'Current time (as epoch).',
                              'version': ''},
                     'total_connections': {'data_type': '32u',
                                           'description': 'Total number of connections opened since the server started running.',
                                           'version': ''},
                     'total_items': {'data_type': '32u',
                                     'description': 'Total number of items stored during the life of this instance.',
                                     'version': ''},
                     'uptime': {'data_type': '32u',
                                'description': 'Uptime (in seconds) for this memcached instance.',
                                'version': ''},
                     'version': {'data_type': 'string',
                                 'description': 'Version string of this instance.',
                                 'version': ''},}
        slabs = {'cas_badval': {'data_type': '',
                                'description': 'Number of CAS hits on this chunk where the existing value did not match',
                                'version': '1.3.x'},
                 'cas_hits': {'data_type': '',
                              'description': 'Number of CAS hits to this chunk',
                              'version': '1.3.x'},
                 'chunk_size': {'data_type': '',
                                'description': 'Space allocated to each chunk within this slab class.',
                                'version': ''},
                 'chunks_per_page': {'data_type': '',
                                     'description': 'Number of chunks within a single page for this slab class.',
                                     'version': ''},
                 'cmd_set': {'data_type': '',
                             'description': 'Number of set commands on this chunk',
                             'version': '1.3.x'},
                 'decr_hits': {'data_type': '',
                               'description': 'Number of decrement hits to this chunk',
                               'version': '1.3.x'},
                 'delete_hits': {'data_type': '',
                                 'description': 'Number of delete hits to this chunk',
                                 'version': '1.3.x'},
                 'free_chunks': {'data_type': '',
                                 'description': 'Number of chunks not yet allocated to items.',
                                 'version': ''},
                 'free_chunks_end': {'data_type': '',
                                     'description': 'Number of free chunks at the end of the last allocated page.',
                                     'version': ''},
                 'get_hits': {'data_type': '',
                              'description': 'Number of get hits to this chunk',
                              'version': '1.3.x'},
                 'incr_hits': {'data_type': '',
                               'description': 'Number of increment hits to this chunk',
                               'version': '1.3.x'},
                 'mem_requested': {'data_type': '',
                                   'description': 'The true amount of memory of memory requested within this chunk',
                                   'version': '1.4.1'},
                 'total_chunks': {'data_type': '',
                                  'description': 'Number of chunks allocated to the slab class.',
                                  'version': ''},
                 'total_pages': {'data_type': '',
                                 'description': 'Number of pages allocated to this slab class.',
                                 'version': ''},
                 'used_chunks': {'data_type': '',
                                 'description': 'Number of chunks allocated to an item..',
                                 'version': ''},
                 'active_slabs': {'data_type': '',
                                 'description': 'Total number of slab classes allocated.',
                                 'version': ''},
                 'total_malloced': {'data_type': '',
                                 'description': 'Total amount of memory allocated to slab pages.',
                                 'version': ''},}
        items = {'age': {'data_type': '',
                         'description': 'The age of the oldest item within the slab class, in seconds.',
                         'version': ''},
                 'evicted': {'data_type': '',
                             'description': 'The number of items evicted to make way for new entries.',
                             'version': ''},
                 'evicted_nonzero': {'data_type': '',
                                     'description': 'The time of the last evicted non-zero entry',
                                     'version': '1.4.0'},
                 'evicted_time': {'data_type': '',
                                  'description': 'The time of the last evicted entry',
                                  'version': ''},
                 'number': {'data_type': '',
                            'description': 'The number of items currently stored in this slab class.',
                            'version': ''},
                 'outofmemory': {'data_type': '',
                                 'description': 'The number of items for this slab class that have triggered an out of memory error (only value when the -M command line option is in effect).',
                                 'version': ''},
                 'tailrepairs': {'data_type': '',
                                 'description': 'Number of times the entries for a particular ID need repairing',
                                 'version': ''},}
        if args:
            if args[0] == 'items':
                return items
            elif args[0] == 'slabs':
                return slabs
        return standard
    
def get_keys(db=None, match_any=False, **kwargs):
    """Fetch all keys matching the given parameters.
    
    :param flush_type: Flush type(s) to filter on. String or list of strings.
    :param module: Module(s) to filter on. String or list of strings.
    :param path: Path(s) to filter on. String or list of strings.
    :param db: Database to filter on. String. Will be set automagically from request.
    :param status_code: Status code(s) to filter on. String or list of strings.
    :param etag: ETag(s) to filter on. String or list of strings.
    :param match_any: Match any of the given criterias (OR method). Otherwise must match all criterias (AND method).
    :param load: Set to True to return mc_load result for all the keys. Will return a dict with key as keys and mc_load result as values.
    """
    if not db:
        db = request.env.cr.dbname
    # List the filter keys we will use
    filter_fields = ('flush_type', 'module', 'path', 'status_code', 'etag')
    load = kwargs.get('load')
    items = MEMCACHED_CLIENT().stats('items')
    slab_limit = {k.split(':')[1]:v for k,v in MEMCACHED_CLIENT().stats('items').items() if k.split(':')[2] == 'number' }
    key_lists = [MEMCACHED_CLIENT().stats('cachedump',slab,str(limit)) for slab,limit in slab_limit.items()]
    keys =  [key for sublist in key_lists for key in sublist.keys()]
    
    # Check if we will perform any filtering and convert filter terms to lists
    filter_active = False
    for field in filter_fields:
        value = kwargs.get(field)
        if value and value != 'all':
            filter_active = True
            if type(value) != list:
                kwargs[field] = [value]
    
    # Load all keys at once
    data = mc_load(keys)
    # Reform keylist. Keys could potentially have disappeared between then and now.
    keys = data.keys()
    # Perform filtering on DB and potentially other fields
    for k in keys:
        key = data[k]
        # Remove other databases
        if key.get('db') != db:
            del data[k]
            continue
        
        # Perform filtering if needed
        if filter_active:
            for field in filter_fields:
                value = kwargs.get(field)
                if value and value != 'all':
                    if match_any:
                        # Use OR method
                        if key.get(field) in value:
                            # One field matched. Save this key.
                            continue
                    
                    else:
                        # Use AND method
                        if key.get(field) not in value:
                            # One field did not match. Delete this key.
                            del data[k]
                            continue
            if match_any:
                # OR method. No filters matched.
                del data[k]
    if load:
        return data
    return data.keys()
    
            # ~ # Filter on flush type
            # ~ if flush_type and flush_type != 'all':
                # ~ if type(flush_type) != list:
                    # ~ flush_type = [flush_type]
                # ~ if match_any:
                    # ~ if key.get('flush_type') in flush_type:
                        # ~ continue
                # ~ else:
                    # ~ if key.get('flush_type') not in flush_type:
                        # ~ del keys[i]
                        # ~ continue
            
            # ~ # Filter on etag
            # ~ if etag and etag != 'all':
                # ~ if type(etag) != list:
                    # ~ etag = [etag]
                # ~ if match_any:
                    # ~ if key.get('etag') in flush_type:
                        # ~ continue
                # ~ else:
                    # ~ if key.get('etag') not in etag:
                        # ~ del keys[i]
                        # ~ continue
            
            # ~ # Filter on module
            # ~ if module and module != 'all':
                # ~ if type(module) != list:
                    # ~ module = [module]
                # ~ if match_any:
                    # ~ if key.get('module') in flush_type:
                        # ~ continue
                # ~ else:
                    # ~ if key.get('module') not in module:
                        # ~ del keys[i]
                        # ~ continue
            
            # ~ # Filter on path
            # ~ if path and path != 'all':
                # ~ if type(path) != list:
                    # ~ path = [path]
                # ~ if match_any:
                    # ~ if key.get('path') in flush_type:
                        # ~ continue
                # ~ else:
                    # ~ if key.get('path') not in path:
                        # ~ del keys[i]
                        # ~ continue
            
            # ~ # Filter on status code
            # ~ if status_code and status_code != 'all':
                # ~ if type(status_code) != list:
                    # ~ status_code = [status_code]
                # ~ if match_any:
                    # ~ if key.get('status_code') in flush_type:
                        # ~ continue
                # ~ else:
                    # ~ if key.get('status_code') not in status_code:
                        # ~ del keys[i]
                        # ~ continue

def get_flush_page(keys, title, url='', delete_url=''):
    def append_key(rows, key, p):
        rows.append((
            '<a href="/mcmeta/%s">%s</a>' %(key, key),
            '<a href="%s">%s</a>' %(p.get('path'), p.get('path')),
            p.get('module', '').replace('openerp.addons.', '').split('.')[0],
            p.get('flush_type'),
            p.get('key_raw'),
            '<a href="/mcpage/%s/delete?url=%s" class="fa fa-trash-o"/>' %(key, url)
        ))
    rows = []
    if type(keys) == dict:
        for key, p in keys.iteritems():
            append_key(rows, key, p)
    else:
        for key in keys:
            append_key(rows, key, mc_load(key))
    
    return request.website.render("website_memcached.memcached_page", {
        'title': title,
        'header': [_('Key'),_('Path'),_('Module'),_('Flush Type'),_('Key Raw'),_('Cmd')],
        'rows': rows,
        'delete_url': delete_url,
        'url': url,
        })


    #~ return '<H1>%s</H1><table>%s</table>' % (title,
        #~ ''.join(['<tr><td><a href="/mcpage/%s/delete">%s (delete)</a></td><td></td><td></td></tr>' % (k,k,p.get('path'),p.get('module'),p.get('flush_type')) for key in keys for p,k in [memcached.MEMCACHED_CLIENT().get(key),key]])
def mc_save(key, page_dict, cache_age):
    if cache_age and cache_age > 2592000:  # 30-days
        # Will be read as a unix timestamp
        cache_age = int(time()) + cache_age
    MEMCACHED_CLIENT().set(key, page_dict, cache_age)
    #~ chunks = [page_dict['page'][i:1000*900] for i in range(int(math.ceil(len(page_dict['page']) / (1000.0*900))))]
    #~ for i,chunk in enumerate(chunks):
        #~ if i == 0:
            #~ page_dict['page'] = chunk
            #~ MEMCACHED_CLIENT().set(key,page_dict,cache_age)
        #~ else:
            #~ MEMCACHED_CLIENT().set('%s-c%d' % (key,i),chunk,cache_age)

def mc_load(key):
    """Load data for the given key(s) from memcache.
    :parameter key: The key(s) that should be loaded. str or list(str).
    :returns: If one key was given, returns the value of that key. If more than one key was given, returns a dict with keys and key values.
    """
    if type(key) == list:
        return MEMCACHED_CLIENT().get_many(key)
    return MEMCACHED_CLIENT().get(key) or {}

def mc_delete(key):
    if type(key) == list:
        MEMCACHED_CLIENT().delete_many(key)
    else:
        MEMCACHED_CLIENT().delete(key)

def mc_flush_all():
    MEMCACHED_CLIENT().flush_all()
    
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
    :param no-store and no-cache "no-cache" indicates that the returned response can't be used to satisfy a subsequent request to the same URL without first checking with the server if the response has changed. As a result, if a proper validation token (ETag) is present, no-cache incurs a roundtrip to validate the cached response, but can eliminate the download if the resource has not changed. By contrast, "no-store" is much simpler. It simply disallows the browser and all intermediate caches from storing any version of the returned response—for example, one containing private personal or banking data. Every time the user requests this asset, a request is sent to the server and a full response is downloaded.
    :param immutable http://bitsup.blogspot.com/2016/05/cache-control-immutable.html
    :param  must-revalidate and proxy-revalidate
    :
    """
    # Default values for routing parameters
    routing = {
        'no_cache': True,
        'must_revalidate': True,
        'proxy_revalidate': True,
    }
    routing.update(kw)
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
            # ~ _logger.warn('\n\npath: %s\n' % request.httprequest.path)
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
                                                    country='%s' % request.env.user.partner_id.commercial_partner_id.country_id.code,
                                                    post='%s' % kw,
                                                    xmlid='%s' % kw.get('xmlid'),
                                                    version='%s' % kw.get('version'),
                                                    is_user='1' if (request.website and request.website.is_user()) else '0',
                                                    employee='1' if request.env.ref('base.group_user') in request.env.user.groups_id else '0',
                                                    publisher='1' if request.env.ref('base.group_website_publisher') in request.env.user.groups_id else '0',
                                                    designer='1' if request.env.ref('base.group_website_designer') in request.env.user.groups_id else '0',
                                                    ).encode('latin-1', 'replace')
                #~ raise Warning(request.env['res.users'].browse(request.uid).group_ids)
                key = str(MEMCACHED_HASH(key_raw))
            else:
                key_raw = ('%s,%s,%s' % (request.env.cr.dbname,request.httprequest.path,request.env.context)).encode('latin-1', 'replace') # Default key
                key = str(MEMCACHED_HASH(key_raw))
                # ~ _logger.warn('\n\ndefault key_raw: %s\nkey: %s\n' % (key_raw, key))

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
                error = clean_text(str(e))
                _logger.warn("MemcacheUnknownError %s key: %s path: %s" % (eror, key, request.httprequest.path))
                return werkzeug.wrappers.Response(status=500,headers=[
                        ('X-CacheKey',key),
                        ('X-CacheError','MemcacheUnknownError %s' %error),
                        ('X-CacheKeyRaw',key_raw),
                        ('Server','Odoo %s Memcached %s' % (common.exp_version().get('server_version'), MEMCACHED_VERSION)),
                        ])
            except MemcacheUnexpectedCloseError as e:
                error = "MemcacheUnexpectedCloseError %s " % e
                _logger.warn(error)
            except Exception as e:
                err = sys.exc_info()
                # ~ error = "Memcached Error %s key: %s path: %s %s" % (e,key,request.httprequest.path, ''.join(traceback.format_exception(err[0], err[1], err[2])))
                error = clean_text(''.join(traceback.format_exception(err[0], err[1], err[2])))
                _logger.warn("Memcached Error %s key: %s path: %s" % (error, key, request.httprequest.path))
                error = clean_text(str(e))
                return werkzeug.wrappers.Response(status=500,headers=[
                        ('X-CacheKey',key),
                        ('X-CacheError','Memcached Error %s' % error),
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
                    #~ view_meta += 'Chunks   : %s<br>' % res['chunks']
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
                # MISS. Render the page.
                # ~ _logger.warn('\n\nMISS. Rendering the page.\n')
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

                if response.template:
                    #~ _logger.error('template %s values %s response %s' % (response.template,response.qcontext,response.response))
                    page = response.render()
                else:
                    page = ''.join(response.response)
                flush_type = routing['flush_type'](kw).lower().encode('ascii', 'replace').replace(' ', '-') if routing.get('flush_type', None) else ""
                page_dict = {
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
                    'status_code': response.status_code,
                    'flush_type': flush_type,
                    'headers': response.headers,
                    }
                if routing.get('no_cache'):
                    page_dict['ETag'] = '%s' % MEMCACHED_HASH(page)
                # ~ _logger.warn('\n\npath: %s\nstatus_code: %s\nETag: %s\n' % (page_dict.get('path'), page_dict.get('status_code'), page_dict.get('ETag')))
                mc_save(key, page_dict, cache_age)
                if flush_type:
                    add_flush_type(request.cr.dbname, flush_type)
                #~ raise Warning(f.__module__,f.__name__,route())
            else:
                # HIT in cache. ETag not checked yet...
                request_dict = {h[0]: h[1] for h in request.httprequest.headers}
                #~ _logger.warn('Page Exists If-None-Match %s Etag %s' %(request_dict.get('If-None-Match'), page_dict.get('ETag')))
                if request_dict.get('If-None-Match') and (request_dict.get('If-None-Match') == page_dict.get('ETag')):
                    # HIT with correct ETag
                    header = [
                        ('X-CacheETag', page_dict.get('ETag')),
                        ('X-CacheKey', key),
                        ('X-Cache', 'from cache'),
                        ('X-CacheKeyRaw', key_raw),
                        ('X-CacheController', page_dict.get('controller_time')),
                        ('X-CacheRender', page_dict.get('render_time')),
                        ('X-CacheCacheAge', cache_age),
                        ('Server', 'Odoo %s Memcached %s' % (common.exp_version().get('server_version'), MEMCACHED_VERSION)),
                        ]
                    # TODO: Do we need this? Odoo provides its own ETag for some files, which cause mixups.
                    #       Might be that these headers are needed when downloading files in /web (we had some such problem earlier).
                    header += [(k,v) for k,v in page_dict.get('headers',[(None,None)])]
                    # ~ _logger.warn('returns 304 headers %s' % header)
                    if page_dict.get('status_code') in [301, 302, 307, 308]:
                        # ~ _logger.warn('\n\nHIT, but weird status_code: %s\n' % page_dict.get('status_code'))
                        return werkzeug.wrappers.Response(status=page_dict['status_code'],headers=header)
                    # ~ _logger.warn('\n\nHIT. ETag matches: %s\n' % request_dict.get('If-None-Match'))
                    return werkzeug.wrappers.Response(status=304,headers=header)
                # HIT, but ETag does not match.
                # ~ _logger.warn('\n\nHIT. ETag did not match.\n')
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
            # ~ _logger.warn('\n\nclean headers: %s\n' % response.headers)
            if page_dict.get('headers'):
                for k,v in page_dict['headers'].items():
                    #~ response.headers.add(k,v)
                    response.headers[k] = v
            # ~ _logger.warn('\n\ndirty headers: %s\n' % response.headers)
            response.headers['Cache-Control'] ='max-age=%s,s-maxage=%s,%s' % (max_age, s_maxage, ','.join([keyword for keyword in ['no-store', 'immutable', 'no-transform', 'no-cache', 'must-revalidate', 'proxy-revalidate'] if routing.get(keyword.replace('-', '_'))] + [routing.get('private', 'public')])) # private: must not be stored by a shared cache.
            if page_dict.get('ETag'):
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
            response.status_code = page_dict.get('status_code', 200)
            # ~ _logger.warn('\n\nfinal headers: %s\n' % response.headers)
            # ~ _logger.warn('\n%s\n' % ''.join(traceback.format_stack()))
            return response

        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    return decorator
