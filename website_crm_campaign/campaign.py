# Copyright (C) 2017-2025 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class CrmTrackingCampaign(models.Model):
    _inherit = 'crm.tracking.campaign'

    website_description = fields.Html(string='Website Description')
    website_published = fields.Boolean(
        string='Available on website', default=False, copy=False)
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = '/campaign/%s' % rec.id

    @api.model
    def get_campaigns(self):
        return super().get_campaigns().filtered(lambda c: c.website_published)


class CrmCampaignObject(models.Model):
    _inherit = 'crm.campaign.object'

    @api.model
    def _selection_object_id(self):
        return super()._selection_object_id() + [
            ('product.public.category', 'Product Category'),
        ]

    @api.onchange('object_id')
    def _onchange_object_id(self):
        res = super()._onchange_object_id()
        if self.object_id and self.object_id._name == 'product.public.category':
            self.name = self.object_id.name
            self.description = self.object_id.description
            self.image = self.object_id.image
        return res


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    description = fields.Text(string='Description')
    mobile_icon = fields.Char(string='Mobile Icon',
        help='This icon will display on smaller devices')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        campaigns = self.env['crm.tracking.campaign'].get_campaigns()
        for vals in vals_list:
            if campaigns and not vals.get('campaign_id'):
                vals['campaign_id'] = campaigns[0].id
        return super().create(vals_list)
