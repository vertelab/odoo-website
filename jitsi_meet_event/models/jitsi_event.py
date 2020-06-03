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
from random import choice
import random
import string
import werkzeug
import re

import logging
_logger = logging.getLogger(__name__)


    
class Event(models.Model):
    _inherit = 'event.event'
    jitsi_id = fields.Many2one(string='Jitsi Event')
    token = fields.Char(string='Token',default=lambda t: t._get_token())

    @api.model
    def _get_token(self):
        return  ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])


class JitsiMeet(models.Model):
    _inherit = 'jitsi_meet.jitsi_meet'



class JitsiMeetExternalParticipant(models.Model):
    _inherit = 'jitsi_meet.external_user'
