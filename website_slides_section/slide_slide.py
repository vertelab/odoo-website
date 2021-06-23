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
import logging

from odoo import models, api, fields, _

_logger = logging.getLogger(__name__)


class Slide(models.Model):
    _inherit = 'slide.slide'

    category_id = fields.Many2one(inverse="_inverse_category_id")

    def _inverse_category_id(self):

        # pass
        for slide in self:
            # xx = slide.slide_ids.filtered(lambda s: s == slide.category_id)
            print('xx', slide)
        # self.category_id = self.category_id.id  # initialize whatever the state

        channel_slides = {}
        for slide in self:
            if slide.channel_id.id not in channel_slides:
                channel_slides[slide.channel_id.id] = slide.channel_id.slide_ids

        for cid, slides in channel_slides.items():
            current_category = self.env['slide.slide']
            slide_list = list(slides)
            slide_list.sort(key=lambda s: (s.sequence, not s.is_category))
            for slide in slide_list:
                if slide.is_category:
                    print(slide.category_id.name)
                    # current_category = slide
                    slide.category_id = current_category.browse(slide).id
                # elif slide.category_id != current_category:
                #     slide.category_id = current_category.id

    #
    # def _inverse_category_id(self):
    #
    #     self.category_id = False  # initialize whatever the state
    #
    #     channel_slides = {}
    #     for slide in self:
    #         if slide.channel_id.id not in channel_slides:
    #             channel_slides[slide.channel_id.id] = slide.channel_id.slide_ids
    #
    #     for cid, slides in channel_slides.items():
    #         current_category = self.env['slide.slide']
    #         slide_list = list(slides)
    #         slide_list.sort(key=lambda s: (s.sequence, not s.is_category))
    #         for slide in slide_list:
    #             if slide.is_category:
    #                 current_category = slide
    #             elif slide.category_id != current_category:
    #                 slide.category_id = current_category.id

