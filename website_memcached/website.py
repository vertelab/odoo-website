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

import logging
_logger = logging.getLogger(__name__)


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
    MEMCACHED_CLIENT = Client(('localhost', 11211), serializer=serializer_pickle, deserializer=deserializer_pickle)
    from pymemcache.client.murmur3 import murmur3_32 as MEMCACHED_HASH
except:
    _logger.info('website_memcached requires pymemcache (pip install pymemcache).')

#~ MEMCACHED_PAGE = {
    #~ '94576762L': {'function': MemCachedController.dn_shop(),}
#~ }

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

    @api.model
    def memcached_render(self,raw_key,function,template,values,ncache=100000):
        key = MEMCACHED_HASH(raw_key)
        #~ MEMCACHED_PAGE[key] = {'function': function,}
        MEMCACHED_CLIENT.set(key,self.render(template,values))
        redirect = werkzeug.utils.redirect('/mcpage/%s' % key,301)  # Permanent redirect
        redirect.autocorrect_location_header = False
        #~ headers.append(('Cache-Control', 'no-cache' if ncache == 0 else 'max-age=%s' % (ncache)))
        return redirect


#
#  1) Controller normal render:      return request.website.render("webshop_dermanord.products", values)
#  2) a key is built by template and values  eg 94576762L, cache rendered page, save original url 94576762L-url
#  3) redirect permanently to special controller /mcpage/94576762L
#  4) every new attempt to load old url will client automatically redirect to cache /dn_shop -> /mcpage/94576762L
#  5) If/when /mcpage/94576762L does not return page, try to recreate page using stored url_and_context
#
# save request.session[xxx] along with page?
# what about SEO?

    @api.multi
    def render(self,template, values=None, status_code=None):
        key = MEMCACHED_HASH((template,values))
        if not MEMCACHED_CLIENT.get(key):
            MEMCACHED_CLIENT.set(key,super(website,self).render(template, values, status_code))
            #~ MEMCACHED_CLIENT.set('%s-url' % key,'/dn_shop')  # save url and context for recreation 
        redirect = werkzeug.utils.redirect('/mcpage/%s' % key,301)  # Permanent redirect
        redirect.autocorrect_location_header = False
        #~ headers.append(('Cache-Control', 'no-cache' if ncache == 0 else 'max-age=%s' % (ncache)))
        return redirect


class MemCachedController(http.Controller):

  @http.route([
        '/mcpage/<string:key>',
    ], type='http', auth="public", website=True)
    def memcached_page(self, key='',**post):
        rendered_page = MEMCACHED_CLIENT.get(key)
        if rendered_page:
            return rendered_page
        url_and_context = MEMCACHED_CLIENT.get('%s-url' % key)
        if url_and_context:
            redirect = werkzeug.utils.redirect(url_and_context,302)  # Temporary redirect
            redirect.autocorrect_location_header = False
            return redirect
        return request.registry['ir.http']._handle_exception(e, 404)
