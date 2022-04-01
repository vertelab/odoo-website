# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.urls import url_quote

from odoo import api, models, fields, tools

SUPPORTED_IMAGE_MIMETYPES = [
    'image/gif', 'image/jpe', 'image/jpeg', 'image/jpg', 'image/gif', 'image/png', 'image/svg+xml'
]


class DMSFile(models.Model):
    _inherit = "dms.file"

    local_url = fields.Char("Attachment URL", compute='_compute_local_url')
    image_src = fields.Char(compute='_compute_image_src')
    image_width = fields.Integer(compute='_compute_image_size')
    image_height = fields.Integer(compute='_compute_image_size')
    original_id = fields.Many2one('dms.file', string="Original (unoptimized, unresized) attachment", index=True)

    def _compute_local_url(self):
        for attachment in self:
            attachment.local_url = f'/web/image/dms.file/{attachment.id}/image_1024'

    @api.depends('mimetype', 'name')
    def _compute_image_src(self):
        for attachment in self:
            # Only add a src for supported images
            if attachment.mimetype not in SUPPORTED_IMAGE_MIMETYPES:
                attachment.image_src = False
                continue

            attachment.image_src = '/web/image/dms.file/%s/image_1024' % attachment.id

    @api.depends('content') 
    def _compute_image_size(self):
        for attachment in self:
            try:
                image = tools.base64_to_image(attachment.content)
                attachment.image_width = image.width
                attachment.image_height = image.height
            except Exception:
                attachment.image_width = 0
                attachment.image_height = 0

    def _get_media_info(self):
        """Return a dict with the values that we need on the media dialog."""
        self.ensure_one()
        return self._read_format(['id', 'name', 'description', 'mimetype', 'checksum', 'extension', 'res_id',
                                  'res_model', 'public', 'image_src', 'image_width', 'image_height',
                                  'original_id'])[0]
