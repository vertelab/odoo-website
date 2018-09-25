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

class EventEvent(models.Model):
    _inherit = 'event.event'
    
    meeting_id = fields.Many2one(string='BBB Meeting', comodel_name='bbb.meeting')
    
    @api.multi
    def action_start_meeting(self):
        if not self.meeting_id:
            raise Warning(_("This event has no meeting."))
        self.meeting_id.action_start_meeting()

    @api.multi
    def action_invite_to_meeting(self):
        if not self.meeting_id:
            raise Warning(_("This event has no meeting."))
        if not self.user_id:
            raise Warning(_("This event has no one responsible for it."))
        if not self.user_id.email:
            raise Warning(_("The person responsible for this event has no email."))
        participants = self.registration_ids.mapped('_participant_ids').filtered(lambda p: p.state not in ['cancel'])
        no_email = participants.mapped('partner_id').filtered(lambda p: not p.email)
        if no_email:
            raise Warning(_("The following participants have no email: %s") % ', '.join([p.name for p in no_email]))
        if not participants:
            raise Warning(_("This event has no participants."))
        template = self.env.ref('website_bbb_event.email_template_participant_invite')
        for participant in participants:
            join_url = self.meeting_id.invite(participant.partner_id.name)
            template.with_context(join_url=join_url).send_mail(participant.id, force_send=True, raise_exception=True)
            
            
            
    
    
