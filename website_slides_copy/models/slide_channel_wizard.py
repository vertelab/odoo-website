from odoo import models, fields, api, _


class SlideChannelWiz(models.TransientModel):
    _name = 'slide.channel.wizard'

    @api.model
    def _get_active_id(self):
        """Simply returns the active id of the channel"""
        return self._context.get('active_id')

    active_slide_channel_id = fields.Many2one('slide.channel', string="Active Course", default=_get_active_id)
    slide_category_id = fields.Many2one('slide.slide', string="Section")
    slide_channel_id = fields.Many2one('slide.channel', string="Course")

    @api.onchange('active_slide_channel_id')
    def _get_slide_categories(self):
        """Performs the onchange api, so as to ge the slide category and show it on slide_category_id field"""
        if self.active_slide_channel_id:
            return {'domain': {'slide_category_id': [
                ('channel_id', '=', self.active_slide_channel_id.id), ('is_category', '=', True)
            ]}}
        else:
            return {'domain': {'slide_category_id': False}}

    def copy_to_selected_channel(self):
        """Copy all slides under the selected category to the slide_channel"""
        category_id = False
        slide_ids = self.env['slide.slide'].search([
            ('channel_id', '=', self.active_slide_channel_id.id),
            ('category_id', '=', self.slide_category_id.id)
        ])

        """Get last sequence of slide channel you are transferring slides to"""
        last_slide_sequence = 0

        channel_slide_ids = self.slide_channel_id.slide_ids.filtered(lambda slide_cat: slide_cat.is_category is False)
        if channel_slide_ids:
            last_slide_sequence = channel_slide_ids[-1].sequence
            last_slide_sequence += 1
        else:
            last_slide_sequence += 0

        # Create Category Section
        if slide_ids[0].category_id:
            category_id = self.env['slide.slide'].create({
                'name': slide_ids[0].category_id.name,
                'is_category': True,
                'channel_id': self.slide_channel_id.id,
                'sequence': last_slide_sequence
            }).id

        # Create Corresponding Slides
        for slide in slide_ids:
            last_slide_sequence += 1
            self.env['slide.slide'].create({
                'channel_id': self.slide_channel_id.id,
                'name': slide.name,
                'active': slide.active,
                'tag_ids': slide.tag_ids.ids,
                'is_preview': slide.is_preview,
                'is_new_slide': slide.is_new_slide,
                'completion_time': slide.completion_time,
                'website_published': slide.website_published,
                'is_published': slide.is_published,
                'website_url': slide.website_url,
                'category_id': category_id,
                'sequence': last_slide_sequence,
                'datas': slide.datas,
                'url': slide.url,
                'document_id': slide.document_id,
                'link_ids': slide.link_ids.ids,
                'slide_type': slide.slide_type,
                'question_ids': slide.question_ids.ids,
                'slide_resource_ids': slide.slide_resource_ids.ids,
                'slide_resource_downloadable': slide.slide_resource_downloadable,
                'html_content': slide.html_content,
                'embed_code': slide.embed_code,
                'embedcount_ids': slide.embedcount_ids.ids,
                'channel_type': slide.channel_type,
                'channel_allow_comment': slide.channel_allow_comment,
            })
