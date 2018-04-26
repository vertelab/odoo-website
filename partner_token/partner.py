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
from odoo import models, fields, api, _
from odoo.addons.web import http
from odoo.http import request
import random
import string
import werkzeug

import logging
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_token(self):
        return  ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

    token = fields.Char(string='Token',default=lambda t: t._get_token())
    
    @api.one
    def send_token(self):
        pass
        
    @api.multi
    def check_token(self,token):
        return bool(self.token == token)
    
    @api.multi
    def redirect_token(self, url):
        #~ redirect_url = '%s?token=%s' % (request.httprequest.base_url, )
        #~ redirect_url = '%s?token=%s' % (request.httprequest.base_url, )
        #~ return """<html><head><script>
            #~ window.location = '%sredirect=' + encodeURIComponent("%s" + location.hash);
        #~ </script></head></html>
        #~ """ % (url, redirect_url)    
        return werkzeug.utils.redirect("%s?token=%s" % (url,self.token), 303)

class partner_token(http.Controller):

    def redirect_token(self, url,token):
        redirect_url = '%s?token=%s' % (request.httprequest.base_url, )
        #~ redirect_url = '%s?token=%s' % (request.httprequest.base_url, )
        #~ return """<html><head><script>
            #~ window.location = '%sredirect=' + encodeURIComponent("%s" + location.hash);
        #~ </script></head></html>
        #~ """ % (url, redirect_url)    
        return werkzeug.utils.redirect("%s?token=%s" % (url,token), 303)
    #~ return http.redirect_with_hash(redirect)
    
    
    @http.route(['/redirect_test',], type='http', auth='public', website=True)
    def redirect_test(self, **post):
        _logger.error('rediect-test')
        return werkzeug.utils.redirect("%s?token=%s" % ('/test','kadjgfajkdgfads'), 303)
    #~ def redirect_with_hash(url, code=303):
    #~ # Most IE and Safari versions decided not to preserve location.hash upon
    #~ # redirect. And even if IE10 pretends to support it, it still fails
    #~ # inexplicably in case of multiple redirects (and we do have some).
    #~ # See extensive test page at http://greenbytes.de/tech/tc/httpredirects/
    #~ if request.httprequest.user_agent.browser in ('firefox',):
        #~ return werkzeug.utils.redirect(url, code)
    #~ if urlparse.urlparse(url, scheme='http').scheme not in ('http', 'https'):
        #~ url = 'http://' + url
    #~ url = url.replace("'", "%27").replace("<", "%3C")
    #~ return "<html><head><script>window.location = '%s' + location.hash;</script></head></html>" % url
