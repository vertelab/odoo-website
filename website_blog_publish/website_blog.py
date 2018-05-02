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
import logging
_logger = logging.getLogger(__name__)

class BlogPost(models.Model):
    _inherit = 'blog.post'

    date_start = fields.Datetime(string="Start date",help="Start/stop-time when this blog post will be published. If stop-time is missing it will not be unpublished")
    date_stop = fields.Datetime(string="Stop date",help="Date and time when this blog post will be unpublished")

    @api.one
    def do_publish(self):
        #~ _logger.error('Cron do_publish %s' % self)
        self.website_published = True

    @api.one
    def do_unpublish(self):
        #~ _logger.error('Cron do_unpublish %s' % self)
        self.website_published = False

    @api.model
    def cron_publish(self):
        for post in self.env['blog.post'].search([('website_published','=',False),('date_start','<=',fields.Datetime.now()),'|',('date_stop','=',False),('date_stop','>',fields.Datetime.now())]):
            post.do_publish() 
        for post in self.env['blog.post'].search([('date_stop','<=',fields.Datetime.now()),('website_published','=',True)]):
            post.do_unpublish() 
        _logger.info('Cron blog publish done')
