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

from openerp import models,  fields,  api,  _
from openerp import http
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)


class Main(http.Controller):

    @http.route(['/website_document_redirect'], type='json', auth='user')
    def website_document_redirect(self, id):
        action = request.env.ref('base.action_attachment').id
        return '/web#id=%s&view_type=form&model=ir.attachment&action=%s' %(id, action)

# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
