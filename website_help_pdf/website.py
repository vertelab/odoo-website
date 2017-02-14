# -*- coding: utf-8 -*-
import cStringIO
import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET

import logging
import re

import werkzeug.utils
import urllib2
import werkzeug.wrappers
from PIL import Image

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import openerp
from openerp.addons.web.controllers.main import WebClient
from openerp.addons.web import http
from openerp.http import request, STATIC_CACHE
from openerp.tools import image_save_for_web
import urllib2

logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)

class Website(openerp.addons.web.controllers.main.Home):

    @http.route('/page/<page:page>', type='http', auth="public", website=True)
    def page(self, page, **opt):
        values = {
            'path': page,
        }
        # /page/website.XXX --> /page/XXX
        if page.startswith('website.'):
            return request.redirect('/page/' + page[8:], code=301)
        elif '.' not in page:
            page = 'website.%s' % page

        try:
            request.website.get_template(page)
        except ValueError, e:
            # page not found
            if request.website.is_publisher():
                page = 'website.page_404'
            else:
                return request.registry['ir.http']._handle_exception(e, 404)

        return request.render(page, values)


class Website_page(models.Model):
    _inherit = "website"

  
    
    def get_template(self, cr, uid, ids, template, context=None):
        if isinstance(template, (int, long)):
            view_id = template
        else:
            if '.' not in template:
                template = 'website.%s' % template
            module, xmlid = template.split('.', 1)
            model, view_id = request.registry["ir.model.data"].get_object_reference(cr, uid, module, xmlid)
        return self.pool["ir.ui.view"].browse(cr, uid, view_id, context=context)

    #~ def _render(self, cr, uid, ids, template, values=None, context=None):
        #~ # TODO: remove this. (just kept for backward api compatibility for saas-3)
        #~ return self.pool['ir.ui.view'].render(cr, uid, template, values=values, context=context)

    #~ def render(self, cr, uid, ids, template, values=None, status_code=None, context=None):
        #~ # TODO: remove this. (just kept for backward api compatibility for saas-3)
        #~ return request.render(template, values, uid=uid)

#~ class HttpRequest(openerp.http.WebRequest):
    #~ """ Handler for the ``http`` request type.

    #~ matched routing parameters, query string parameters, form_ parameters
    #~ and files are passed to the handler method as keyword arguments.

    #~ In case of name conflict, routing parameters have priority.

    #~ The handler method's result can be:

    #~ * a falsy value, in which case the HTTP response will be an
      #~ `HTTP 204`_ (No Content)
    #~ * a werkzeug Response object, which is returned as-is
    #~ * a ``str`` or ``unicode``, will be wrapped in a Response object and
      #~ interpreted as HTML

    #~ .. _form: http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.2
    #~ .. _HTTP 204: http://tools.ietf.org/html/rfc7231#section-6.3.5
    #~ """
    #~ _request_type = "http"

    #~ def __init__(self, *args):
        #~ super(HttpRequest, self).__init__(*args)
        #~ params = self.httprequest.args.to_dict()
        #~ params.update(self.httprequest.form.to_dict())
        #~ params.update(self.httprequest.files.to_dict())
        #~ params.pop('session_id', None)
        #~ self.params = params

    #~ def _handle_exception(self, exception):
        #~ """Called within an except block to allow converting exceptions
           #~ to abitrary responses. Anything returned (except None) will
           #~ be used as response."""
        #~ try:
            #~ return super(HttpRequest, self)._handle_exception(exception)
        #~ except SessionExpiredException:
            #~ if not request.params.get('noredirect'):
                #~ query = werkzeug.urls.url_encode({
                    #~ 'redirect': request.httprequest.url,
                #~ })
                #~ return werkzeug.utils.redirect('/web/login?%s' % query)
        #~ except werkzeug.exceptions.HTTPException, e:
            #~ return e

    #~ def dispatch(self):
        #~ if request.httprequest.method == 'OPTIONS' and request.endpoint and request.endpoint.routing.get('cors'):
            #~ headers = {
                #~ 'Access-Control-Max-Age': 60 * 60 * 24,
                #~ 'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode'
            #~ }
            #~ return Response(status=200, headers=headers)

        #~ r = self._call_function(**self.params)
        #~ if not r:
            #~ r = Response(status=204)  # no content
        #~ return r

    #~ def make_response(self, data, headers=None, cookies=None):
        #~ """ Helper for non-HTML responses, or HTML responses with custom
        #~ response headers or cookies.

        #~ While handlers can just return the HTML markup of a page they want to
        #~ send as a string if non-HTML data is returned they need to create a
        #~ complete response object, or the returned data will not be correctly
        #~ interpreted by the clients.

        #~ :param basestring data: response body
        #~ :param headers: HTTP headers to set on the response
        #~ :type headers: ``[(name, value)]``
        #~ :param collections.Mapping cookies: cookies to set on the client
        #~ """
        #~ response = Response(data, headers=headers)
        #~ if cookies:
            #~ for k, v in cookies.iteritems():
                #~ response.set_cookie(k, v)
        #~ return response

    #~ def render(self, template, qcontext=None, lazy=True, **kw):
        #~ """ Lazy render of a QWeb template.

        #~ The actual rendering of the given template will occur at then end of
        #~ the dispatching. Meanwhile, the template and/or qcontext can be
        #~ altered or even replaced by a static response.

        #~ :param basestring template: template to render
        #~ :param dict qcontext: Rendering context to use
        #~ :param bool lazy: whether the template rendering should be deferred
                          #~ until the last possible moment
        #~ :param kw: forwarded to werkzeug's Response object
        #~ """
        #~ raise Warning('Hello')
        #~ response = Response(template=template, qcontext=qcontext, **kw)
        #~ if not lazy:
            #~ return response.render()
        #~ return response



class view(models.Model):
    _inherit = 'ir.ui.view'

    pdf_file = fields.Binary(string="PDF-file")


class Reports(http.Controller):
    POLLING_DELAY = 0.25
    TYPES_MAPPING = {
        'doc': 'application/vnd.ms-word',
        'html': 'text/html',
        'odt': 'application/vnd.oasis.opendocument.text',
        'pdf': 'application/pdf',
        'sxw': 'application/vnd.sun.xml.writer',
        'xls': 'application/vnd.ms-excel',
    }

    @http.route('/web/report', type='http', auth="user")
    @serialize_exception
    def index(self, action, token):
        action = simplejson.loads(action)

        report_srv = request.session.proxy("report")
        context = dict(request.context)
        context.update(action["context"])

        report_data = {}
        report_ids = context.get("active_ids", None)
        if 'report_type' in action:
            report_data['report_type'] = action['report_type']
        if 'datas' in action:
            if 'ids' in action['datas']:
                report_ids = action['datas'].pop('ids')
            report_data.update(action['datas'])

        report_id = report_srv.report(
            request.session.db, request.session.uid, request.session.password,
            action["report_name"], report_ids,
            report_data, context)

        report_struct = None
        while True:
            report_struct = report_srv.report_get(
                request.session.db, request.session.uid, request.session.password, report_id)
            if report_struct["state"]:
                break

            time.sleep(self.POLLING_DELAY)

        report = base64.b64decode(report_struct['result'])
        if report_struct.get('code') == 'zlib':
            report = zlib.decompress(report)
        report_mimetype = self.TYPES_MAPPING.get(
            report_struct['format'], 'octet-stream')
        file_name = action.get('name', 'report')
        if 'name' not in action:
            reports = request.session.model('ir.actions.report.xml')
            res_id = reports.search([('report_name', '=', action['report_name']),],
                                    context=context)
            if len(res_id) > 0:
                file_name = reports.read(res_id[0], ['name'], context)['name']
            else:
                file_name = action['report_name']
        file_name = '%s.%s' % (file_name, report_struct['format'])

        return request.make_response(report,
             headers=[
                 ('Content-Disposition', content_disposition(file_name)),
                 ('Content-Type', report_mimetype),
                 ('Content-Length', len(report))],
             cookies={'fileToken': token})


    @http.route('/web/binary/image', type='http', auth="public")
    def image(self, model, id, field, **kw):
        last_update = '__last_update'
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context
        headers = [('Content-Type', 'image/png')]
        etag = request.httprequest.headers.get('If-None-Match')
        hashed_session = hashlib.md5(request.session_id).hexdigest()
        retag = hashed_session
        id = None if not id else simplejson.loads(id)
        if type(id) is list:
            id = id[0] # m2o
        try:
            if etag:
                if not id and hashed_session == etag:
                    return werkzeug.wrappers.Response(status=304)
                else:
                    date = Model.read(cr, uid, [id], [last_update], context)[0].get(last_update)
                    if hashlib.md5(date).hexdigest() == etag:
                        return werkzeug.wrappers.Response(status=304)

            if not id:
                res = Model.default_get(cr, uid, [field], context).get(field)
                image_base64 = res
            else:
                res = Model.read(cr, uid, [id], [last_update, field], context)[0]
                retag = hashlib.md5(res.get(last_update)).hexdigest()
                image_base64 = res.get(field)

            if kw.get('resize'):
                resize = kw.get('resize').split(',')
                if len(resize) == 2 and int(resize[0]) and int(resize[1]):
                    width = int(resize[0])
                    height = int(resize[1])
                    # resize maximum 500*500
                    if width > 500: width = 500
                    if height > 500: height = 500
                    image_base64 = openerp.tools.image_resize_image(base64_source=image_base64, size=(width, height), encoding='base64', filetype='PNG')

            image_data = base64.b64decode(image_base64)

        except Exception:
            image_data = self.placeholder()
        headers.append(('ETag', retag))
        headers.append(('Content-Length', len(image_data)))
        try:
            ncache = int(kw.get('cache'))
            headers.append(('Cache-Control', 'no-cache' if ncache == 0 else 'max-age=%s' % (ncache)))
        except:
            pass
        return request.make_response(image_data, headers)


    @api.cr_uid_ids_context
    def render(self, cr, uid, id_or_xml_id, values=None, engine='ir.qweb', context=None):
        return request.make_response(report,
             headers=[
                 ('Content-Disposition', "attachment; filename=%s" % urllib2.quote(filename.encode('utf8')),
                 ('Content-Type', 'application/pdf'),
                 ('Content-Length', len(report))],
             cookies={'fileToken': token})

        raise Warning('ir.ui.view render', id_or_xml_id)
        if isinstance(id_or_xml_id, list):
            id_or_xml_id = id_or_xml_id[0]

        if not context:
            context = {}

        if values is None:
            values = dict()
        qcontext = dict(
            env=api.Environment(cr, uid, context),
            keep_query=keep_query,
            request=request, # might be unbound if we're not in an httprequest context
            debug=request.debug if request else False,
            json=simplejson,
            quote_plus=werkzeug.url_quote_plus,
            time=time,
            datetime=datetime,
            relativedelta=relativedelta,
        )
        qcontext.update(values)

        # TODO: This helper can be used by any template that wants to embedd the backend.
        #       It is currently necessary because the ir.ui.view bundle inheritance does not
        #       match the module dependency graph.
        def get_modules_order():
            if request:
                from openerp.addons.web.controllers.main import module_boot
                return simplejson.dumps(module_boot())
            return '[]'
        qcontext['get_modules_order'] = get_modules_order

        def loader(name):
            return self.read_template(cr, uid, name, context=context)

        return self.pool[engine].render(cr, uid, id_or_xml_id, qcontext, loader=loader, context=context)
