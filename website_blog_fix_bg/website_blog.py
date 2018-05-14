# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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
from openerp import http
from openerp.http import request
from openerp.addons.website_blog.controllers.main import WebsiteBlog

import logging
_logger = logging.getLogger(__name__)

class WebsiteBlog(WebsiteBlog):

    @http.route('/blogpost/change_background', type='json', auth="public", website=True)
    def change_bg(self, post_id=0, image=None, **post):
        if not post_id:
            return False
        import logging
        if image:
            image_split = image.split('/')
            if len(image_split) > 3:
                image = '/%s' % '/'.join(image_split[3:])
        return request.registry['blog.post'].write(request.cr, request.uid, [int(post_id)], {'background_image': image}, request.context)


