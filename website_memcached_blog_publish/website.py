# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website_blog.controllers.main import QueryURL, WebsiteBlog

import logging
_logger = logging.getLogger(__name__)


class BlogPost(models.Model):
    _inherit = 'blog.post'

    @api.one
    def do_publish(self):
        super(BlogPost, self).do_publish()
        self.mc_delete_post(self)

    @api.one
    def do_unpublish(self):
        super(BlogPost, self).do_unpublish()
        self.mc_delete_post(self)

    @api.model
    def mc_delete_post(self,post):
        #~ _logger.error('mc_delete_post %s %s' % (memcached.get_keys(flush_type=post.blog_id.name.replace(u'å', 'a').replace(u'ä', 'a').replace(u'ö', 'o').replace(' ', '-')),post.blog_id.name.replace(u'å', 'a').replace(u'ä', 'a').replace(u'ö', 'o').replace(' ', '-')))
        if post and post.blog_id:
            for key in memcached.get_keys(flush_type='blog-%s' % post.blog_id.name.replace(u'å', 'a').replace(u'ä', 'a').replace(u'ö', 'o').replace(' ', '-').lower()):
                memcached.mc_delete(key) 

    @api.multi
    def write(self, values):
        res = super(BlogPost, self).write(values)
        for o in self:
            self.mc_delete_post(o)
        return res

