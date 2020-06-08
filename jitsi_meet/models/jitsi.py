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
    date = fields.Datetime('Date', required=True)
    date_delay = fields.Float('Duration', required=True, default=1.0)
    participants = fields.Many2many('res.users', string='Participant', required=True, default=_get_default_participant)
    external_participants = fields.One2many('jitsi_meet.external_user', 'meet', string='External Participant')
    url = fields.Char(string='URL to Meeting', compute='_compute_url')
    closed = fields.Boolean('Closed', default=False)
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    
 
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
        return []

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
    partner_id = fields.Many2one(related='meet.create_uid.partner_id')
    meeting_date = fields.Datetime(related='meet.date', string='Meeting Date')
    meeting_name = fields.Char(related='meet.name', string='Meeting Name')
    meeting_url = fields.Char(related='meet.url',string='Meeting URL')
    send_mail = fields.Boolean('Send Invitation', default=True)
    mail_sent = fields.Boolean('Invitation Sent', readonly=True, default=False)
    date_formated = fields.Char(compute='_format_date')

    def _format_date(self):
        for part in self:
            part.date_formated = fields.Datetime.from_string(
                part.meeting_date).strftime('%m/%d/%Y, %H:%M:%S')

    @api.model
    def create(self, vals):

        res = super(JitsiMeetExternalParticipant, self).create(vals)
        if res.send_mail:
            template = self.env.ref('jitsi_meet.email_template_edi_jitsi_meet')
            self.env['mail.template'].sudo().browse(template.id).send_mail(res.id)
            res.sudo().write({'mail_sent': True})
        return res

    @api.multi
    def write(self, vals):
        if 'send_mail' in vals and vals.get('send_mail'):
            if not self.mail_sent:
                template = self.env.ref('jitsi_meet.email_template_edi_jitsi_meet')
                template.send_mail(self.id)
                vals.update({'mail_sent': True})
        return super(JitsiMeetExternalParticipant, self).write(vals)

class JitsiMeetModel(models.AbstractModel):
    _name = 'jitsi_meet.model'

    jitsi_token = fields.Char(string='Jitsi Token')
    jitsi_id = fields.Many2one(comodel_name='jitsi_meet.jitsi_meet', string='Jitsi Meeting')

    @api.model
    def get_jitsi_meetings(self, token):
        return self.sudo().search([('jitsi_token', '=', token), ('jitsi_id', '!=', False)])
    
    @api.multi
    def get_jitsi_user_info(self):
        self.ensure_one()
        return {'name': None, 'partner_id': None, 'user:id': None}
