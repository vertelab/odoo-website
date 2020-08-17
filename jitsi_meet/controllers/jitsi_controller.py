# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2020 Vertel AB (<http://vertel.se>).
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
from openerp.exceptions import Warning, ValidationError
from openerp import http
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)

class JitsiController(http.Controller):

    @http.route(['/jitsi/lobby', '/jitsi/lobby/<token>'], auth='public', type='http', website=True)
    def lobby(self, token=None, **post):
        participants = request.env['jitsi_meet.external_user'].sudo().find_jitsi_participants(token)

        values = {
            'participants': participants,
        }
        return request.website.render('jitsi_meet.lobby', values)



