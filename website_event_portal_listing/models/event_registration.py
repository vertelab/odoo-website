# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.tools import format_datetime
from odoo.exceptions import AccessError, ValidationError
from collections import ChainMap


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'mail.thread', 'mail.activity.mixin']

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super(EventRegistration, self).create(vals_list)
        if registrations._check_auto_confirmation():
            registrations.sudo().action_confirm()

        partner_ids = registrations.partner_id + registrations.attendee_partner_id + registrations.event_id.organizer_id

        if partner_ids:
            registrations.message_subscribe(partner_ids=partner_ids.ids)
            registrations.event_id.message_subscribe(partner_ids=partner_ids.ids)

        return registrations
