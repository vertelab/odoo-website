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

    jitsi_id = fields.Many2one(comodel_name='jitsi_meet.jitsi_meet', string='Jitsi Event')
    
    @api.multi
    def create_jitsi(self):
        self.jitsi_id = self.env["jitsi_meet.jitsi_meet"].create({
            'name': self.name,
            'date': self.date_begin,
            'participants': self.user_id or self.env.user,
        })
        return self.jitsi_id
    
    @api.multi
    def open_jitsi(self):
        return {'name': 'JITSI MEET',
                #'res_model': 'ir.actions.act_url', 
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': self.jitsi_id.url,
                }
    
    def delete_jitsi(self):
        self.jitsi_id.unlink()

class EventParticipant(models.Model):
    _inherit = ['event.participant', 'jitsi_meet.model']
    _name = 'event.participant'

    jitsi_id = fields.Many2one(related='event_id.jitsi_id')

    @api.multi
    def get_jitsi_user_info(self):
        self.ensure_one()
        return {
            'name': None,
            'partner_id': None,
            'user_id': None}

class JitsiMeet(models.Model):
    _inherit = 'jitsi_meet.jitsi_meet'

    @api.model
    def get_jitsi_meeting_models(self):
        res = super(JitsiMeet, self).get_jitsi_meeting_models()
        res.append('event.participant')
        return res

class JitsiMeetExternalParticipant(models.Model):
    _inherit = 'jitsi_meet.external_user'
