# Copyright (C) 2017-2025 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class CrmCampaignObject(models.Model):
    _inherit = 'crm.campaign.object'

    @api.model
    def _selection_object_id(self):
        return super()._selection_object_id() + [
            ('blog.post', 'Blog Post'),
        ]

    @api.onchange('object_id')
    def _onchange_object_id(self):
        res = super()._onchange_object_id()
        if self.object_id and self.object_id._name == 'blog.post':
            self.name = self.object_id.name
            self.description = self.object_id.subtitle
            try:
                match = re.search(
                    r'ir\.attachment/(.+?)_',
                    self.object_id.background_image or ''
                )
                if match:
                    attachment = self.env['ir.attachment'].browse(
                        int(match.group(1)))
                    self.image = attachment.datas
            except (AttributeError, ValueError):
                self.image = None
        return res
