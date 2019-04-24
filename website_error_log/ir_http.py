# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017 Vertel AB (<http://vertel.se>).
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

import openerp
from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError
from openerp.http import request
from openerp.addons.base.ir import ir_qweb

from openerp.addons.website.models.ir_http import ir_http as website_ir_http

import werkzeug
import traceback

import logging
logger = logging.getLogger(__name__)

class ir_http(models.AbstractModel):
    _inherit = 'ir.http'
    
    def _handle_exception(self, exception, code=500):
        """Replacement of _handle_exception from website module."""
        is_website_request = bool(getattr(request, 'website_enabled', False) and request.website)
        if not is_website_request:
            request.env['website.error.log'].log_error(request, None, -1, None)
            # Don't touch non website requests exception handling
            return super(website_ir_http, self)._handle_exception(exception)
        else:
            try:
                response = super(website_ir_http, self)._handle_exception(exception)
                if isinstance(response, Exception):
                    exception = response
                else:
                    request.env['website.error.log'].log_error(request, response, -2, None)
                    # if parent excplicitely returns a plain response, then we don't touch it
                    return response
            except Exception, e:
                exception = e

            values = dict(
                exception=exception,
                traceback=traceback.format_exc(exception),
            )
            code = getattr(exception, 'code', code)

            if isinstance(exception, openerp.exceptions.AccessError):
                code = 403

            if isinstance(exception, ir_qweb.QWebException):
                values.update(qweb_exception=exception)
                if isinstance(exception.qweb.get('cause'), openerp.exceptions.AccessError):
                    code = 403

            if isinstance(exception, werkzeug.exceptions.HTTPException) and code is None:
                # Hand-crafted HTTPException likely coming from abort(),
                # usually for a redirect response -> return it directly
                request.env['website.error.log'].log_error(request, None, -3, values)
                return exception

            if code == 500:
                logger.error("500 Internal Server Error:\n\n%s", values['traceback'])
                if 'qweb_exception' in values:
                    view = request.registry.get("ir.ui.view")
                    views = view._views_get(request.cr, request.uid, exception.qweb['template'],
                                            context=request.context)
                    to_reset = [v for v in views if v.model_data_id.noupdate is True and not v.page]
                    values['views'] = to_reset
            elif code == 403:
                logger.warn("403 Forbidden:\n\n%s", values['traceback'])

            values.update(
                status_message=werkzeug.http.HTTP_STATUS_CODES[code],
                status_code=code,
            )

            if not request.uid:
                self._auth_method_public()
            
            request.env['website.error.log'].log_error(request, None, code, values)
            try:
                html = request.website._render('website.%s' % code, values)
            except Exception:
                html = request.website._render('website.http_error', values)
            return werkzeug.wrappers.Response(html, status=code, content_type='text/html;charset=utf-8')
