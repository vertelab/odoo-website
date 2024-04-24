# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides


class WebsiteSlidesScorm(WebsiteSlides):

    @http.route('/slides/slide/get_scorm_version', type="json", auth="public", website=True)
    def get_scorm_version(self, slide_id):
        slide_dict = self._fetch_slide(slide_id)
        return {
            'scorm_version': slide_dict['slide'].scorm_version
        }

    @http.route('/slide/slide/set_session_info', type='json', auth="user", website=True)
    def _set_session_info(self, slide_id, element, value):
        slide_partner_sudo = request.env['slide.slide.partner'].sudo()
        slide_id = request.env['slide.slide'].browse(slide_id)
        slide_partner_id = slide_partner_sudo.search([
            ('slide_id', '=', slide_id.id),
            ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if not slide_partner_id:
            slide_partner_id = slide_partner_sudo.create({
                'slide_id': slide_id.id,
                'channel_id': slide_id.channel_id.id,
                'partner_id': request.env.user.partner_id.id
            })
        session_element_id = slide_partner_id.lms_session_info_ids.filtered(lambda l: l.name == element)
        if session_element_id:
            session_element_id.value = value
        else:
            request.env['lms.session.info'].create({
                'name': element,
                'value': value,
                'slide_partner_id': slide_partner_id.id
            })

    @http.route('/slide/slide/get_session_info', type='json', auth="user", website=True)
    def _get_session_info(self, slide_id):
        slide_partner_sudo = request.env['slide.slide.partner'].sudo()
        slide_id = request.env['slide.slide'].browse(slide_id)
        slide_partner_id = slide_partner_sudo.search([
            ('slide_id', '=', slide_id.id),
            ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        session_info_ids = request.env['lms.session.info'].search([
            ('slide_partner_id', '=', slide_partner_id.id)
        ])
        values = {}
        for session_info in session_info_ids:
            values[session_info.name] = session_info.value
        return values

    @http.route('/slides/slide/set_completed_scorm', website=True, type="json", auth="public")
    def slide_set_completed_scorm(self, slide_id, completion_type):
        if request.website.is_public_user():
            return {'error': 'public_user'}
        fetch_res = self._fetch_slide(slide_id)
        slide = fetch_res['slide']
        if fetch_res.get('error'):
            return fetch_res
        if slide.website_published and slide.channel_id.is_member:
            slide.action_mark_completed()
        self._set_karma_points(fetch_res['slide'], completion_type)
        return {
            'channel_completion': fetch_res['slide'].channel_id.completion
        }

    def _set_karma_points(self, slide_id, completion_type):
        slide_partner_sudo = request.env['slide.slide.partner'].sudo()
        slide_partner_id = slide_partner_sudo.search([
            ('slide_id', '=', slide_id.id),
            ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if slide_partner_id:
            user_sudo = request.env['res.users'].sudo()
            user_id = user_sudo.search([('partner_id', '=', slide_partner_id.partner_id.id)], limit=1)
            if completion_type == 'passed':
                slide_partner_id.lms_scorm_karma = slide_id.scorm_passed_xp
                user_id.karma = slide_id.scorm_passed_xp
            if completion_type == 'completed':
                slide_partner_id.lms_scorm_karma = slide_id.scorm_completed_xp
                user_id.karma = slide_id.scorm_passed_xp