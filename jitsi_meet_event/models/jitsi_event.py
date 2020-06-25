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
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

class Event(models.Model):
    _inherit = ['event.event', 'jitsi_meet.model']
    _name = 'event.event'

    jitsi_id = fields.Many2one(comodel_name='jitsi_meet.jitsi_meet', string='Jitsi Event')
    
    @api.model
    def get_jitsi_meeting_model_data(self):
        """Fields to sync with Jitsi Meeting."""
        return {
            # Map fields on this model to Jitsi meeting.
            'field_map': {
                'date_begin': 'date',
                'date_end': 'date_end',
                'name': 'name',
            },
        }
    
    @api.multi
    def create_jitsi(self):
        self.jitsi_id = self.env["jitsi_meet.jitsi_meet"].create({
            'name': self.name,
            'date': self.date_begin,
            'date_end': self.date_end,
            'participants': self.user_id or self.env.user,
            'url': self.website_url,
        })
        # jitsi email template sent to email confirmation
        # self.email_confirmation_id=self.env.ref('jitsi_meet_event.email_template_jitsi_event_invite').id
        return self.jitsi_id

    @api.multi
    def open_jitsi(self):
        return {
            'name': 'JITSI MEET',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': self.jitsi_id.url,
        }

    @api.multi
    def delete_jitsi(self):
        self.jitsi_id.unlink()

class EventParticipant(models.Model):
    _inherit = ['event.participant', 'jitsi_meet.participant.model']
    _name = 'event.participant'
    
    @api.model
    def get_jitsi_participant_model_data(self):
        """Fields to sync with Jitsi Participant."""
        return {
            'mail_template': 'jitsi_meet_event.email_template_jitsi_event_invite',
            # Map fields on this model to Jitsi participant.
            'field_map': {
                # event       # jitsi     
                'partner_id': 'partner_id'
            },

        }
    
    @api.one
    def create_delete_jitsi_participant(self):
        """Create a jitsi participant from this event participant."""
        if self.jitsi_participant_id:
            return
        if self.event_id.jitsi_id and self.state == 'open':
            self.jitsi_participant_id = self.env['jitsi_meet.external_user'].create({
                'meet': self.event_id.jitsi_id.id,
                'name': self.partner_id.email,
            })

class JitsiMeet(models.Model):
    _inherit = 'jitsi_meet.jitsi_meet'

    meeting_object = fields.Reference(selection_add=[('event.event', 'Event')])

    @api.model
    def get_jitsi_meeting_models(self):
        models = super(JitsiMeet, self).get_jitsi_meeting_models()
        models.add('event.participant')
        return models

    @api.model
    def get_jitsi_meetings_domain(self):
        domain = super(JitsiMeet, self).get_jitsi_meetings_domain()
        date_limit = fields.Datetime.from_string(fields.Datetime.now())
        date_limit -= timedelta(hours=int(
            self.env['ir.config_parameter'].get_param(
                'jitsi_meet_event.date_limit', '168')))
        domain.append(('date_end', '>', fields.Datetime.to_string(date_limit)))
        return domain

class JitsiMeetExternalParticipant(models.Model):
    _inherit = 'jitsi_meet.external_user'

    participant_object = fields.Reference(selection_add=[('event.participant', 'Event Participant')])
