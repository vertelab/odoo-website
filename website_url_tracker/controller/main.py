# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2019- Vertel AB (<http://vertel.se>).
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
import werkzeug
import logging
_logger = logging.getLogger(__name__)


class Main(http.Controller):

    @http.route(['/goto/<int:partner_id>/<string:field>'], type='http', auth='public', website=True)
    def goto(self, partner_id=0, field='', **post):
        def partner_url_field(partner, f):
            try:
                return getattr(partner, f)
            except:
                return False
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if partner:
            url = partner_url_field(partner, field)
            if url:
                request.env['website.url.tracker'].sudo().create({
                    'timestamp': fields.Datetime.now(),
                    'user_id': request.env.user.id,
                    'partner_id': partner.id,
                })
                if 'http://' not in url:
                    if 'https://' not in url:
                        url = 'http://' + url
                return request.redirect(url)
            else:
                return request.redirect('/')
        else:
            return request.redirect('/')
