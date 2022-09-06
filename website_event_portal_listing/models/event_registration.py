# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.tools import format_datetime
from odoo.exceptions import AccessError, ValidationError


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'event.registration']
