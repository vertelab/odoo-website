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
from openerp.exceptions import Warning
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
        wizard = self.env['bbb.join.wizard'].create({
            'meeting_id': self.id
        })
        return {
            'name': _('Join Meeting'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bbb.join.wizard',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard.id,
        }

    @api.multi
    def invite_partners(self, template, partners, moderator=False):
        for partner in partners:
            join_url = self.invite(partner.name, moderator)
            template.with_context(join_url=join_url).send_mail(partner.id, force_send=True, raise_exception=True)

class BBBJoinWizard(models.TransientModel):
    _name = 'bbb.join.wizard'
    _description = 'Big Blue Button Join Wizard'
    
    meeting_id = fields.Many2one(string='Meeting', comodel_name='bbb.meeting', required=True)
    name = fields.Char('Name')
    
    @api.multi
    def action_join(self):
        url = self.meeting_id.invite(self.name, True)
        return {
            'type': 'ir.actions.act_url',
            'url':url,
            'target': 'new',
        }
