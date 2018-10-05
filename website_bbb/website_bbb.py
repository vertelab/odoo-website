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

from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)

import urllib
import urllib2
import sha
import uuid
from xml.etree import ElementTree
import traceback
import sys

class BBBServer(models.Model):
    _name = 'bbb.server'
    _description = 'Big Blue Button Server'
    
    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL', required=True)
    secret = fields.Char(string='Secret', required=True)
    

class BBBMeeting(models.Model):
    _name = 'bbb.meeting'
    _description = 'Big Blue Button Meeting'

    def _default_bbbid(self):
        return uuid.uuid4()

    def _default_server_id(self):
        return self.env['bbb.server'].search([], limit=1)

    name = fields.Char(string='Name', required=True)
    welcome = fields.Char(string='Welcome Message', required=True)
    bbbid = fields.Char(string='BBB ID', default=_default_bbbid, required=True)
    password = fields.Char(string='Password', help='Password for regular meeting attendees')
    mod_password = fields.Char(string='Moderator Password', help='Password for moderators', required=True)
    server_id = fields.Many2one(string='Server', comodel_name='bbb.server', required=True, default=_default_server_id)

    @api.multi
    def get_checksum(self, func, params):
        return sha.new(func + params + self.server_id.secret).hexdigest()

    @api.multi
    def get_url(self, func, **params):
        for p in params:
            if type(params[p]) == unicode:
                params[p] =  params[p].encode('utf-8')
        param_str = urllib.urlencode(params)
        checksum = self.get_checksum(func, param_str)
        param_str += '&checksum=%s'%  checksum
        return '%s/bigbluebutton/api/%s?%s' % (self.server_id.url, func, param_str)

    @api.multi
    def start_meeting(self):
        url = self.get_url('create', name=self.name, meetingID=self.bbbid, attendeePW=self.password, moderatorPW=self.mod_password, welcome=self.welcome)
        res = ""
        try:
            res = urllib2.urlopen(url).read()
            return ElementTree.fromstring(res).find('returncode').text == 'SUCCESS'
        except:
            tb = ''.join(traceback.format_exception(*sys.exc_info()))
            _logger.warn("Failed to start Big Blue Button Meeting\n\nReply:%s\n%s" % (res, tb))
            return False

    @api.multi
    def action_start_meeting(self):
        if self.start_meeting():
            raise Warning(_("Meeting started."))
        raise Warning(_("Failed to start meeting!"))

    @api.multi
    def invite(self, name, moderator=False):
        return self.get_url('join', fullName=name, meetingID=self.bbbid, password=moderator and self.mod_password or self.password)

    @api.multi
    def action_join(self):
        url = self.invite(self.env.user.name, True)
        return {
            'type': 'ir.actions.act_url',
            'url':url,
            'target': 'new',
        }

    @api.multi
    def invite_partners(self, template, partners, moderator=False):
        for partner in partners:
            join_url = self.invite(partner.name, moderator)
            template.with_context(join_url=join_url).send_mail(partner.id, force_send=True, raise_exception=True)

    @api.multi
    def action_invite_wizard(self):
        wizard = self.env['bbb.invite.wizard'].create({
            'meeting_id': self.id
        })
        return {
            'name': _('Send Meeting Invites'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bbb.invite.wizard',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard.id,
        }

class BBBInviteWizard(models.TransientModel):
    _name = 'bbb.invite.wizard'
    _description = 'Big Blue Button Invite Wizard'
    
    meeting_id = fields.Many2one(string='Meeting', comodel_name='bbb.meeting', required=True)
    invite_line_ids = fields.One2many(string='Invitations', comodel_name='bbb.invite.wizard.line', inverse_name='wizard_id')
    message = fields.Char()

    @api.multi
    def action_invite(self):
        action = {
            'name': _('Send Meeting Invites'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bbb.invite.wizard',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
        if not self.invite_line_ids:
            self.message = _("No invitations specified.")
            return action
        no_email = []
        for invitation in self.invite_line_ids:
            if not invitation.email:
                no_email.append(invitation.name)
        _logger.warn(no_email)
        if no_email:
            self.message = _("The following participants have no email: %s") % ', '.join(no_email)
            return action
        template = self.env.ref('website_bbb.email_template_invite_wizard')
        for invitation in self.invite_line_ids:
            template.send_mail(invitation.id, force_send=True, raise_exception=True)
        self.message = _("Emails sent.")
        return action

class BBBInviteWizardLine(models.TransientModel):
    _name = 'bbb.invite.wizard.line'
    _description = 'Big Blue Button Invitation'
    
    name = fields.Char(required=True)
    email = fields.Char()
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner')
    wizard_id = fields.Many2one(string='Wizard', comodel_name='bbb.invite.wizard')
    join_url = fields.Char(string='Invite Link')
    moderator = fields.Boolean(string='Moderator')
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.name
            self.email = self.partner_id.email
            self.join_url = self.wizard_id.meeting_id.invite(self.name)
    
    @api.onchange('name', 'moderator')
    def onchange_name(self):
        if self.name:
            self.join_url = self.wizard_id.meeting_id.invite(self.name, self.moderator)
    
