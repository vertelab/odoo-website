# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from cStringIO import StringIO
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.addons.web.controllers.main import WebClient
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
import base64
import werkzeug

import logging
_logger = logging.getLogger(__name__)

class view(models.Model):
    _inherit = 'ir.ui.view'
    
    pdf_file = fields.Binary(string="PDF-file")

#~ class Reports(http.Controller):
    #~ POLLING_DELAY = 0.25
    #~ TYPES_MAPPING = {
        #~ 'doc': 'application/vnd.ms-word',
        #~ 'html': 'text/html',
        #~ 'odt': 'application/vnd.oasis.opendocument.text',
        #~ 'pdf': 'application/pdf',
        #~ 'sxw': 'application/vnd.sun.xml.writer',
        #~ 'xls': 'application/vnd.ms-excel',
    #~ }

    #~ @http.route('/web/report', type='http', auth="user")
    #~ @serialize_exception
    #~ def index(self, action, token):
        #~ action = simplejson.loads(action)

        #~ report_srv = request.session.proxy("report")
        #~ context = dict(request.context)
        #~ context.update(action["context"])

        #~ report_data = {}
        #~ report_ids = context.get("active_ids", None)
        #~ if 'report_type' in action:
            #~ report_data['report_type'] = action['report_type']
        #~ if 'datas' in action:
            #~ if 'ids' in action['datas']:
                #~ report_ids = action['datas'].pop('ids')
            #~ report_data.update(action['datas'])

        #~ report_id = report_srv.report(
            #~ request.session.db, request.session.uid, request.session.password,
            #~ action["report_name"], report_ids,
            #~ report_data, context)

        #~ report_struct = None
        #~ while True:
            #~ report_struct = report_srv.report_get(
                #~ request.session.db, request.session.uid, request.session.password, report_id)
            #~ if report_struct["state"]:
                #~ break

            #~ time.sleep(self.POLLING_DELAY)

        #~ report = base64.b64decode(report_struct['result'])
        #~ if report_struct.get('code') == 'zlib':
            #~ report = zlib.decompress(report)
        #~ report_mimetype = self.TYPES_MAPPING.get(
            #~ report_struct['format'], 'octet-stream')
        #~ file_name = action.get('name', 'report')
        #~ if 'name' not in action:
            #~ reports = request.session.model('ir.actions.report.xml')
            #~ res_id = reports.search([('report_name', '=', action['report_name']),],
                                    #~ context=context)
            #~ if len(res_id) > 0:
                #~ file_name = reports.read(res_id[0], ['name'], context)['name']
            #~ else:
                #~ file_name = action['report_name']
        #~ file_name = '%s.%s' % (file_name, report_struct['format'])

        #~ return request.make_response(report,
             #~ headers=[
                 #~ ('Content-Disposition', content_disposition(file_name)),
                 #~ ('Content-Type', report_mimetype),
                 #~ ('Content-Length', len(report))],
             #~ cookies={'fileToken': token})


    #~ @http.route('/web/binary/image', type='http', auth="public")
    #~ def image(self, model, id, field, **kw):
        #~ last_update = '__last_update'
        #~ Model = request.registry[model]
        #~ cr, uid, context = request.cr, request.uid, request.context
        #~ headers = [('Content-Type', 'image/png')]
        #~ etag = request.httprequest.headers.get('If-None-Match')
        #~ hashed_session = hashlib.md5(request.session_id).hexdigest()
        #~ retag = hashed_session
        #~ id = None if not id else simplejson.loads(id)
        #~ if type(id) is list:
            #~ id = id[0] # m2o
        #~ try:
            #~ if etag:
                #~ if not id and hashed_session == etag:
                    #~ return werkzeug.wrappers.Response(status=304)
                #~ else:
                    #~ date = Model.read(cr, uid, [id], [last_update], context)[0].get(last_update)
                    #~ if hashlib.md5(date).hexdigest() == etag:
                        #~ return werkzeug.wrappers.Response(status=304)

            #~ if not id:
                #~ res = Model.default_get(cr, uid, [field], context).get(field)
                #~ image_base64 = res
            #~ else:
                #~ res = Model.read(cr, uid, [id], [last_update, field], context)[0]
                #~ retag = hashlib.md5(res.get(last_update)).hexdigest()
                #~ image_base64 = res.get(field)

            #~ if kw.get('resize'):
                #~ resize = kw.get('resize').split(',')
                #~ if len(resize) == 2 and int(resize[0]) and int(resize[1]):
                    #~ width = int(resize[0])
                    #~ height = int(resize[1])
                    #~ # resize maximum 500*500
                    #~ if width > 500: width = 500
                    #~ if height > 500: height = 500
                    #~ image_base64 = openerp.tools.image_resize_image(base64_source=image_base64, size=(width, height), encoding='base64', filetype='PNG')

            #~ image_data = base64.b64decode(image_base64)

        #~ except Exception:
            #~ image_data = self.placeholder()
        #~ headers.append(('ETag', retag))
        #~ headers.append(('Content-Length', len(image_data)))
        #~ try:
            #~ ncache = int(kw.get('cache'))
            #~ headers.append(('Cache-Control', 'no-cache' if ncache == 0 else 'max-age=%s' % (ncache)))
        #~ except:
            #~ pass
        #~ return request.make_response(image_data, headers)


    #~ @api.cr_uid_ids_context
    #~ def render(self, cr, uid, id_or_xml_id, values=None, engine='ir.qweb', context=None):
        #~ return request.make_response(report,
             #~ headers=[
                 #~ ('Content-Disposition', "attachment; filename=%s" % urllib2.quote(filename.encode('utf8')),
                 #~ ('Content-Type', 'application/pdf'),
                 #~ ('Content-Length', len(report))],
             #~ cookies={'fileToken': token})

        #~ raise Warning('ir.ui.view render', id_or_xml_id)
        #~ if isinstance(id_or_xml_id, list):
            #~ id_or_xml_id = id_or_xml_id[0]

        #~ if not context:
            #~ context = {}

        #~ if values is None:
            #~ values = dict()
        #~ qcontext = dict(
            #~ env=api.Environment(cr, uid, context),
            #~ keep_query=keep_query,
            #~ request=request, # might be unbound if we're not in an httprequest context
            #~ debug=request.debug if request else False,
            #~ json=simplejson,
            #~ quote_plus=werkzeug.url_quote_plus,
            #~ time=time,
            #~ datetime=datetime,
            #~ relativedelta=relativedelta,
        #~ )
        #~ qcontext.update(values)

        #~ # TODO: This helper can be used by any template that wants to embedd the backend.
        #~ #       It is currently necessary because the ir.ui.view bundle inheritance does not
        #~ #       match the module dependency graph.
        #~ def get_modules_order():
            #~ if request:
                #~ from openerp.addons.web.controllers.main import module_boot
                #~ return simplejson.dumps(module_boot())
            #~ return '[]'
        #~ qcontext['get_modules_order'] = get_modules_order

        #~ def loader(name):
            #~ return self.read_template(cr, uid, name, context=context)

        #~ return self.pool[engine].render(cr, uid, id_or_xml_id, qcontext, loader=loader, context=context)
    #~ pdf_filename = fields.Char(string="PDF-file")
    
    @api.cr_uid_ids_context
    def render(self, cr, uid, id_or_xml_id, values=None, engine='ir.qweb', context=None):
        if isinstance(id_or_xml_id, list):
            id_or_xml_id = id_or_xml_id[0]
        if isinstance(id_or_xml_id, basestring):
            module, xmlid = id_or_xml_id.split('.', 1)
            model, view_id = self.pool["ir.model.data"].get_object_reference(cr, uid, module, xmlid)
            view_vals = self.pool[model].read(cr, uid, view_id, ['pdf_file'], context)
            if view_vals['pdf_file']:
                response = werkzeug.wrappers.Response()
                data = view_vals['pdf_file']
                #response.set_etag(hashlib.sha1(data).hexdigest())
                response.make_conditional(request.httprequest)

                data = data.decode('base64')
                data = StringIO(data)
                #~ response.mimetype = Image.MIME[image.format]

                filename = '%s.pdf' % xmlid
                response.headers['Content-Disposition'] = 'inline; filename="%s"' % filename

                response.data = data

                return response
                
                #~ res = request.make_response(base64.b64decode(view_vals['pdf_file']),
                            #~ [('Content-Type', 'application/octet-stream'),
                             #~ ('Content-Disposition', content_disposition('%s.pdf' % xmlid))])
                #~ return res
                #~ return StringIO(base64.b64decode(view_vals['pdf_file']))
        return super(view, self).render(cr, uid, id_or_xml_id, values=values, engine=engine, context=context)
        

