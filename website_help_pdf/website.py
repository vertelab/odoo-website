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
        
