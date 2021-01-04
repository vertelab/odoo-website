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

import odoo
from odoo import http
from odoo.http import request
from odoo.addons.website_memcached import memcached
from odoo.addons.website.controllers.main import Website as WebsiteOld
from odoo import models, fields, api, _
import traceback

import logging
_logger = logging.getLogger(__name__)


class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'
    
    memcached_time = fields.Datetime(string='Memcached Timestamp', default=lambda *args, **kwargs: fields.Datetime.now(), help="Last modification relevant to memcached.")
    
    @api.model
    def memcached_update_timestamp(self, res_ids=None):
        """Update the timestamp on the given views and all related views."""
        res_ids = res_ids or []
        done = []
        view_ids = res_ids
        try:
            while view_ids:
                # ~ _logger.warn('done %s' % done)
                # ~ _logger.warn('view_ids %s' % view_ids)
                domain = [('model', '=', self._name), ('res_id', 'in', view_ids)]
                # Find all xml_ids connected to these views
                xml_ids = ['%s.%s' % (v['module'], v['name']) for v in self.env['ir.model.data'].sudo().search_read(domain, ['module', 'name'])]
                # ~ _logger.warn('xml_ids %s' % xml_ids)
                # Find any views that these views inherit from
                domain = [('id', 'in', view_ids), ('inherit_id', '!=', False), ('id', 'not in', done)]
                next_view_ids = [v['inherit_id'][0] for v in self.sudo().search_read(domain, ['inherit_id'])]
                # ~ _logger.warn('next_view_ids %s' % next_view_ids)
                done += view_ids
                # Find any views that make t-call to these views
                domain = []
                for xml_id in xml_ids:
                    domain.append(('arch', 'like', '%%t-call="%s"%%' % xml_id))
                    domain.append(('arch', 'like', "%%t-call='%s'%%" % xml_id))
                domain = ['|' for i in range(len(domain) - 1)] + domain
                domain.append(('id', 'not in', done + next_view_ids))
                # ~ _logger.warn('domain %s' % domain)
                view_ids = next_view_ids + [v['id'] for v in self.sudo().search_read(domain, ['id'])]
                # ~ _logger.warn('view_ids %s' % view_ids)
        except Exception as e:
            _logger.warn(traceback.format_exc(e))
        # In case things get fucky above
        done = done or res_ids
        self.sudo().browse(done).with_context(memcached_no_update_timestamp=True).write({'memcached_time': fields.Datetime.now()})
    
    def write(self, values):
        res = super(ir_ui_view, self).write(values)
        if not self.env.context.get('memcached_no_update_timestamp'):
            view_ids = self.filtered(lambda view: view.type == 'qweb')._ids
            if view_ids:
                self.memcached_update_timestamp(view_ids)
        return res

class ir_translation(models.Model):
    _inherit = 'ir.translation'

    def write(self, vals):
        res = super(ir_translation, self).write(vals)
        self.memcached_view_translation_update()
        return res

    def memcached_view_translation_update(self):
        view_ids = []
        for trans in self:
            if trans.name == 'website':
                view_ids.append(trans.res_id)
        if view_ids:
            # ~ _logger.warn(view_ids)
            self.env['ir.ui.view'].memcached_update_timestamp(view_ids)

class Website(models.Model):
    _inherit = 'website'
    
    def get_dn_groups(self):
        groups = [g.id for g in request.env.user.commercial_partner_id.access_group_ids]
        if self.env.ref('webshop_dermanord.group_dn_ht').id in groups: # Webbplatsbehörigheter / Hudterapeut
            return u'hudterapeut'
        elif self.env.ref('webshop_dermanord.group_dn_spa').id in groups: # Webbplatsbehörigheter / SPA-Terapeut
            return u'SPA-terapeut'
        elif self.env.ref('webshop_dermanord.group_dn_af').id in groups: # Webbplatsbehörigheter / Återförsäljare
            return u'Återförsäljare'
        elif self.env.ref('webshop_dermanord.group_dn_sk').id in groups: # Webbplatsbehörigheter / slutkonsument
            return u'Slutkonsument'
        else:
            return u''
            
    # ~ @http.route(['/my/reseller/<int:reseller_id>'], type='http', auth='user', website=True)
    def reseller_info_update(self):
        reseller_id = request.env.user.agents[0].id if len(request.env.user.agents) > 0 else ''
        
        return ('%s' %reseller_id)
    
    @api.model
    def memcached_get_page_timestamp(self, page):
        time = ''
        try:
        # ~ if True:
            model, view_id = request.env["ir.model.data"].get_object_reference('website', page)
            time = request.env['ir.ui.view'].search_read([('id', '=', view_id)], ['memcached_time'])[0]['memcached_time']
        except:
            pass
        return time

class CachedWebsite(WebsiteOld):

    #~ @http.route('/page/<page:page>', type='http', auth="public", website=True)
    @memcached.route(
        flush_type=lambda kw: 'page',
        key=lambda kw: '{db},/page/%s,{employee},{logged_in},{publisher},{designer},{lang} %s %s %s' % (
            kw.get('page') or '',
            request.website.memcached_get_page_timestamp(kw.get('page')), request.website.get_dn_groups(),request.website.reseller_info_update()))
    def page(self, page, **opt):
        return super(CachedWebsite, self).page(page, **opt)

    #~ @http.route(['/robots.txt'], type='http', auth="public")
    @memcached.route(flush_type=lambda kw: 'page_meta')
    def robots(self):
        return super(CachedWebsite, self).robots()

    #~ @http.route('/sitemap.xml', type='http', auth="public", website=True)
    @memcached.route(flush_type=lambda kw: 'page_meta')
    def sitemap_xml_index(self):
        return super(CachedWebsite, self).sitemap_xml_index()

    #~ @http.route('/website/info', type='http', auth="public", website=True)
    @memcached.route(flush_type=lambda kw: 'page_meta')
    def website_info(self):
        return super(CachedWebsite, self).website_info()

    #~ @http.route([
        #~ '/website/image',
        #~ '/website/image/<model>/<id>/<field>',
        #~ '/website/image/<model>/<id>/<field>/<int:max_width>x<int:max_height>'
        #~ ], auth="public", website=True, multilang=False)
    @memcached.route(flush_type=lambda kw: 'page_image',binary=True, key=lambda k: '{db}{path}')
    def website_image(self, model, id, field, max_width=None, max_height=None):
        #~ raise Warning(model,id,field)
        return super(CachedWebsite, self).website_image(model, id, field, max_width, max_height)

    #------------------------------------------------------
    # Server actions
    #------------------------------------------------------
    #~ @http.route([
        #~ '/website/action/<path_or_xml_id_or_id>',
        #~ '/website/action/<path_or_xml_id_or_id>/<path:path>',
        #~ ], type='http', auth="public", website=True)
    #~ @memcached.route(flush_type='actions_server')
    #~ def actions_server(self, path_or_xml_id_or_id, **post):
        #~ return super(CachedWebsite, self).actions_server(path_or_xml_id_or_id, **post)


class CachedBinary(odoo.addons.web.controllers.main.Binary):

    #~ @http.route([
        #~ '/web/binary/company_logo',
        #~ '/logo',
        #~ '/logo.png',
    #~ ], type='http', auth="none", cors="*")
    @memcached.route(flush_type=lambda kw: 'page_image', binary=True)
    def company_logo(self, dbname=None, **kw):
        return super(CachedBinary, self).company_logo(dbname, **kw)


class CachedHome(odoo.addons.web.controllers.main.Home):

    #~ @http.route([
        #~ '/web/js/<xmlid>',
        #~ '/web/js/<xmlid>/<version>',
    #~ ], type='http', auth='public')
    #~ @memcached.route(flush_type='js_bundle',binary=True,cache_age=60*60*24*30,max_age=604800)
    #~ def js_bundle(self, xmlid, version=None, **kw):
        #~ return super(CachedHome, self).js_bundle(xmlid, version, **kw)
    #~ @http.route([/web/js/website.assets_frontend/6
        #~ '/web/js/<xmlid>',
        #~ '/web/js/<xmlid>/<version>',
    #~ ], type='http', auth='public')
    #~ @memcached.route(['/web/js/website.assets_frontend/<version>',
                      #~ '/web/js/web.assets_common/<version>',
                      #~ '/web/js/website.assets_editor/<version>'],flush_type='js_bundle',binary=True,cache_age=60*60*24*30,max_age=604800)
    #~ def js_bundle_special(self, version=None, **kw):
        #~ if 'website.assets_frontend' in request.httprequest.path:
            #~ return super(CachedHome, self).js_bundle('website.assets_frontend', version, **kw)
        #~ if 'web.assets_common' in request.httprequest.path:
            #~ return super(CachedHome, self).js_bundle('web.assets_common', version, **kw)
        #~ if 'website.assets_editor' in request.httprequest.path:
            #~ return super(CachedHome, self).js_bundle('website.assets_editor', version, **kw)

    @memcached.route(
        flush_type=lambda kw: 'js_bundle',
        binary=True,
        cache_age=60*60*24*30,
        max_age=604800)
    def js_bundle(self, xmlid, version=None, **kw):
        return super(CachedHome, self).js_bundle(xmlid, version, **kw)



    #~ @http.route([
        #~ '/web/css/<xmlid>',
        #~ '/web/css/<xmlid>/<version>',
        #~ '/web/css.<int:page>/<xmlid>/<version>',
    #~ ], type='http', auth='public')
    @memcached.route(
        flush_type=lambda kw: 'css_bundle',
        binary=True,
        cache_age=60*60*24*30,
        max_age=604800,
        content_type="text/css; charset=utf-8;")
    def css_bundle(self, xmlid, version=None, page=None, **kw):
        return super(CachedHome, self).css_bundle(xmlid, version, page, **kw)

class MemCachedController(http.Controller):
    @http.route(['/remove_cached_page',], type='json', auth="user", website=True)
    def remove_cached_page(self, url='',**kw):
        memcached.mc_delete(memcached.get_keys(flush_type='page', path=url))
        return 'deleted'
