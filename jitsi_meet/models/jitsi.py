# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2020 Vertel AB (<http://vertel.se>), Sinerkia ID (<https://www.sinerkia.com>).
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
import string
import werkzeug
import re
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)


def create_hash():
    size = 32
    values = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    p = ''
    p = p.join([choice(values) for i in range(size)])
    return p

def _get_default_participant(self):
    result = []
    result.append(self.env.user.id)
    return [(6, 0, result)]

class JitsiMeet(models.Model):
    _name = 'jitsi_meet.jitsi_meet'
    _description = 'Jitsi Meeting'
    _order = 'date desc'

    name = fields.Char('Meeting Name', required=True)
    hash = fields.Char('Hash')
    date = fields.Datetime('Start Date', required=True)
    date_formated = fields.Char(string='Start Date', compute='_format_date')
    date_end = fields.Datetime('End Date')
    date_end_formated = fields.Char(string='End Date', compute='_format_date_end')
    date_delay = fields.Float('Duration', required=True, default=1.0)
    participants = fields.Many2many('res.users', string='Participants', required=True, default=_get_default_participant)
    external_participants = fields.One2many('jitsi_meet.external_user', 'meet', string='External Participants')
    url = fields.Char(string='URL to Meeting', compute='_compute_url')
    closed = fields.Boolean('Closed', default=False)
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    meeting_object = fields.Reference(selection=[], string='Meeting Object', help="Meeting object connected to this Jitsi meeting.")

    def _format_date(self):
        for part in self:
            part.date_formated = fields.Datetime.from_string(
                part.date).strftime('%Y-%m-%d, %H:%M')

    def _format_date_end(self):
        for part in self:
            part.date_end_formated = fields.Datetime.from_string(
                part.date_end).strftime('%Y-%m-%d, %H:%M')
    
 
    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user

    @api.model
    def create(self, vals):

        vals['hash'] = create_hash()
        res = super(JitsiMeet, self).create(vals)

        return res

    def action_close_meeting(self):
        self.write({'closed': True})

    def action_reopen_meeting(self):
        self.write({'closed': False})

    def open(self):
        return {'name': 'JITSI MEET',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': self.url
                }

    @api.model
    def _compute_url(self):
        config_url = self.env['ir.config_parameter'].sudo().get_param(
            'jitsi_meet.jitsi_meet_url',
            default='https://meet.jitsi.it/')
        for r in self:
            if r.hash and r.name:
                r.url = config_url + r.hash

    @api.model
    def get_jitsi_meeting_models(self):
        return set()

    @api.model
    def find_meetings(self, token):
        res = []
        for model in self.get_jitsi_meeting_models():
            meetings = self.env[model].get_jitsi_meetings(token)
            if meetings:
                res.append(meetings)
        return res

class JitsiMeetExternalParticipant(models.Model):
    _name = 'jitsi_meet.external_user'
    _description = 'Jitsi Meeting External Participant'
    _order = 'name'

    name = fields.Char('Email')
    meet = fields.Many2one('jitsi_meet.jitsi_meet', string='Meeting')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner') # Eh? What is the point of this?
    meeting_date = fields.Datetime(related='meet.date', string='Meeting Date')
    meeting_date_end = fields.Datetime(related='meet.date_end', string='Meeting End Date')
    meeting_name = fields.Char(related='meet.name', string='Meeting Name')
    meeting_url = fields.Char(related='meet.url',string='Meeting URL')
    send_mail = fields.Boolean('Send Invitation', default=True)
    mail_sent = fields.Boolean('Invitation Sent', readonly=True, default=False)
    date_formated = fields.Char(compute='_format_date')
    date_end_formated = fields.Char(compute='_format_date_end')
    participant_object = fields.Reference(selection=[], string='Participant Object', help="Meeting object connected to this Jitsi meeting.")
    jitsi_token = fields.Char(string='Jitsi Token', compute='create_jitsi_token', store=True)
    jitsi_state = fields.Selection(selection=[('planned', 'Planned'),('current','Current'), ('finished','Finished')], compute="compute_jitsi_state")

    @api.one
    @api.depends('meet')
    def create_jitsi_token(self):
        """Create a new token for this Jitsi object."""
        if self.meet and not self.jitsi_token:
            self.jitsi_token = create_hash()

    @api.one
    def compute_jitsi_state(self):
        state = 'planned'
        now = fields.Datetime.from_string(fields.Datetime.now())
        td = timedelta(minutes=int(self.env['ir.config_parameter'].sudo().get_param('jitsi_meet.timedelta', default='10')))
        starttime = fields.Datetime.from_string(self.meeting_date) - td
        endtime = fields.Datetime.from_string(self.meeting_date_end) + td
        if now < starttime:
            state = 'planned'
        elif now > endtime:
            state = 'finished'
        else:
            state = 'current'
        self.jitsi_state = state

    def _format_date(self):
        for part in self:
            part.date_formated = fields.Datetime.from_string(
                part.meeting_date).strftime('%m/%d/%Y, %H:%M:%S')

    def _format_date_end(self):
        for part in self:
            part.date_end_formated = fields.Datetime.from_string(
                part.meeting_date_end).strftime('%m/%d/%Y, %H:%M:%S')

    @api.model
    def create(self, vals):
        res = super(JitsiMeetExternalParticipant, self).create(vals)
        if res.send_mail:
            res.send_invite_email()
            res.sudo().write({'mail_sent': True})
        return res

    @api.multi
    def write(self, vals):
        res = super(JitsiMeetExternalParticipant, self).write(vals)
        if 'send_mail' in vals and vals.get('send_mail'):
            if not self.mail_sent:
                self.send_invite_email()
                self.write({'mail_sent': True})
        return res

    @api.one
    def send_invite_email(self):
        template_name = None
        if self.participant_object:
            template_name = self.participant_object.get_jitsi_participant_model_data()['mail_template']
        if template_name:
            # Send model specific mail
            template = self.env.ref(template_name).sudo()
            template.send_mail(self.participant_object.id)
        else:
            # Send generic mail
            template = self.env.ref('jitsi_meet.email_template_edi_jitsi_meet').sudo()
            template.send_mail(self.id)

    @api.model
    def find_jitsi_participants(self, token):
        """Return  jitsi particiants to show meetings in the lobby."""
        # Time limit to skip ancient meetings.
        date_limit = fields.Datetime.from_string(fields.Datetime.now())
        date_limit -= timedelta(hours=int(
            self.env['ir.config_parameter'].get_param(
                'jitsi_meet.date_limit', '168')))
        domain = [
            ('meet.date_end', '>=', fields.Datetime.to_string(date_limit))]
        if token:
            domain.append(('jitsi_token', '=', token))
        # Should probably make a better connection to user.
        # Can a user change their email to fish for meetings?
        # ~ elif self.env.user.email:
            # ~ domain.append(('name', '=', self.env.user.email))
        else:
            # Not enough data to search participants
            return self
        return self.sudo().search(domain)

class JitsiMeetModel(models.AbstractModel):
    _name = 'jitsi_meet.model'
    _description = 'Jitsi Meeting Model'

    jitsi_id = fields.Many2one(comodel_name='jitsi_meet.jitsi_meet', string='Jitsi Meeting')

    @api.model
    def get_jitsi_meeting_model_data(self):
        """Fields to sync with Jitsi Meeting."""
        return {
            # Map fields on this model to Jitsi meeting.
            'field_map': {},
            # Example:
            # 'field_map': {
            #     'date_start': 'date',
            #     'date_end': 'date_end',
            #     'name': 'name',
            # }
        }

    @api.multi
    def _get_jitsi_meetings(self):
        """Return all jitsi meetings connected to this recordset."""
        values = ['%s,%s' % (self._name, id) for id in self._ids]
        return self.env['jitsi_meet.jitsi_meet'].sudo().search([('meeting_object', 'in', values)])

    @api.one
    def update_jitsi_meeting_values(self):
        """Update values on linked Jitsi Meeting."""
        if not self.jitsi_id:
            return
        self.jitsi_id.meeting_object = '%s,%s' % (self._name, self.id)
        jitsi_data = self.get_jitsi_meeting_model_data()
        for field, jitsi_field in jitsi_data['field_map'].iteritems():
            setattr(self.jitsi_id, jitsi_field, getattr(self, field))

    @api.multi
    def unlink(self):
        """Delete Jitsi meetings together with object."""
        jitsi_meetings = self._get_jitsi_meetings()
        jitsi_meetings and jitsi_meetings.unlink()
        return super(JitsiMeetModel, self).unlink()

    @api.multi
    def write(self, values):
        """Update Jitsi meetings together with object."""
        res = super(JitsiMeetModel, self).write(values)
        if 'jitsi_id' in values:
            # Update connected meetings
            sudo_self = self.sudo()
            for record in sudo_self:
                record.jitsi_id and record.update_jitsi_meeting_values()
            # Delete mettings disconnected from their objects
            for record in sudo_self:
                meetings = record._get_jitsi_meetings() - record.jitsi_id
                meetings and meetings.unlink()
        elif any([f in values for f in self.get_jitsi_meeting_model_data()['field_map']]):
            for record in self.sudo():
                record.jitsi_id and record.update_jitsi_meeting_values()
        return res

    @api.model
    def create(self, values):
        """Connect Jitsi meeting to object upon creation."""
        res = super(JitsiMeetModel, self).create(values)
        if res.jitsi_id:
            res.jitsi_id.meeting_object = '%s,%s' % (res._name, res.id)
        return res

class JitsiMeetParticipantModel(models.AbstractModel):
    _name = 'jitsi_meet.participant.model'

    jitsi_participant_id = fields.Many2one(comodel_name='jitsi_meet.external_user')

    @api.model
    def get_jitsi_participant_model_data(self):
        """Fields to sync with Jitsi Participant."""
        return {
            'mail_template': None,
            # Map fields on this model to Jitsi meeting.
            'field_map': {},
            # Example:
            # 'field_map': {
            #     'date_start': 'date',
            #     'date_end': 'date_end',
            #     'name': 'name',
            # }
        }

    @api.multi
    def _get_jitsi_participants(self):
        """Return all jitsi participants connected to this recordset."""
        values = ['%s,%s' % (self._name, id) for id in self._ids]
        return self.env['jitsi_meet.external_user'].sudo().search([('participant_object', 'in', values)])

    @api.one
    def update_jitsi_meeting_values(self):
        """Update values on linked Jitsi participant."""
        if not self.jitsi_participant_id:
            return
        self.jitsi_participant_id.participant_object = '%s,%s' % (self._name, self.id)
        jitsi_data = self.get_jitsi_participant_model_data()
        for field, jitsi_field in jitsi_data['field_map'].iteritems():
            setattr(self.jitsi_participant_id, jitsi_field, getattr(self, field))

    @api.one
    def create_delete_jitsi_participant(self):
        """Create or delete a jitsi participant from this object.
        Override and implement functionality.
        Check if participant should be created. Create if necessary.
        Check if participant should be deleted. Delete if necessary."""
        return

    @api.multi
    def unlink(self):
        """Delete Jitsi participants together with objects."""
        jitsi_participants = self._get_jitsi_participants()
        jitsi_participants and jitsi_participants.unlink()
        return super(JitsiMeetParticipantModel, self).unlink()

    @api.multi
    def write(self, values):
        """Update Jitsi participants together with objects."""
        res = super(JitsiMeetParticipantModel, self).write(values)
        if 'jitsi_participant_id' in values:
            # Update connected participants
            self_sudo = self.sudo()
            for record in self_sudo:
                record.jitsi_participant_id and record.update_jitsi_meeting_values()
            # Delete participants disconnected from their objects
            for record in self_sudo:
                participants = record._get_jitsi_participants() - record.jitsi_participant_id
                participants and participants.unlink()
        elif any([f in values for f in self.get_jitsi_participant_model_data()['field_map']]):
            for record in self.sudo():
                record.jitsi_participant_id and record.update_jitsi_meeting_values()
        self.create_delete_jitsi_participant()
        return res

    @api.model
    def create(self, values):
        """Connect Jitsi meeting to object upon creation."""
        res = super(JitsiMeetParticipantModel, self).create(values)
        if res.jitsi_participant_id:
            res.jitsi_participant_id.participant_object = '%s,%s' % (res._name, res.id)
        res.create_delete_jitsi_participant()
        return res
