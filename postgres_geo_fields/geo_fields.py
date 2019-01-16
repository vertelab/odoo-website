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
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.osv import fields as old_fields

import logging
_logger = logging.getLogger(__name__)

class GeoFields(models.AbstractModel):
    _name = 'postgres.geo.fields'
    _description = 'Geo Fields'

    _geo_fields = []

    def _auto_init(self, cr, context=None):
        """

        Call _field_create and, unless _auto is False:

        - create the corresponding table in database for the model,
        - possibly add the parent columns in database,
        - possibly add the columns 'create_uid', 'create_date', 'write_uid',
          'write_date' in database if _log_access is True (the default),
        - report on database columns no more existing in _columns,
        - remove no more existing not null constraints,
        - alter existing database columns to match _columns,
        - create database tables to match _columns,
        - add database indices to match _columns,
        - save in self._foreign_keys a list a foreign keys to create (see
          _auto_end).

        """
        res = super(GeoFields, self)._auto_init(cr, context)
        columns = self._select_column_data(cr)
        for field in self._geo_fields:
            if field['name'] not in columns:
                cr.execute('ALTER TABLE "%s" ADD COLUMN "%s" %s' % (self._table, field['name'], field['type']))

    @api.multi
    def get_geo_field(self, field):
        self.env.cr.execute('SELECT %s FROM %s WHERE id=%s' %(field, self._table, self.id))
        return self.env.cr.dictfetchone()[field]

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(GeoFields, self).create(vals)
        for field in self._geo_fields:
            if field.get('compute') and hasattr(self, field['compute']):
                present = False
                for dependency in field.get('depends', []):
                    if dependency in vals:
                        present = True
                        break
                if present:
                    res._recompute_geofields(field['name'])
        return res

    @api.multi
    def write(self, vals):
        res = super(GeoFields, self).write(vals)
        for field in self._geo_fields:
            if field.get('compute') and hasattr(self, field['compute']):
                present = False
                for dependency in field.get('depends', []):
                    if dependency in vals:
                        present = True
                        break
                if present:
                    self._recompute_geofields(field['name'])
        return res

    @api.one
    def _recompute_geofields(self, field):
        for f in self._geo_fields:
            if f['name'] == field:
                if f.get('compute') and hasattr(self, f['compute']):
                    pos = getattr(self, f['compute'])()
                    query = 'UPDATE "%s" SET "%s" = %%s WHERE id = %%s' % (self._table, field)
                    params = [str(pos), self.id]
                    self.env.cr.execute(query, params)

    @api.model
    def geo_search(self, field, position, domain=None, distance=None, limit=10):
        domain = domain or []
        for f in self._geo_fields:
            if f['name'] == field:
                query_obj = self._where_calc(domain)
                self._apply_ir_rules(query_obj, 'read')
                query_obj.where_clause.append('''"%s"."%s" IS NOT NULL''' % (self._table, field))
                if distance:
                    query_obj.where_clause.append('''"%s"."%s" <-> %%s < %%s''' % (self._table, field))
                from_clause, where_clause, params = query_obj.get_sql()
                if distance:
                    params.append(str(position))
                    params.append(distance)
                #~ query = "SELECT id, (%s <@> %%s) FROM %s ORDER BY %s <-> %%s LIMIT %%s" % (field, self._table, field)
                query = """SELECT id FROM %s WHERE %s ORDER BY "%s"."%s" <-> %%s LIMIT %%s""" % (from_clause, where_clause, self._table, field)
                #~ params = [str(position), str(position), limit]
                params += [str(position), limit]
                _logger.warn(query)
                _logger.warn(params)
                self.env.cr.execute(query, params)
                values = self.env.cr.dictfetchall()
                return [v['id'] for v in values]

    @api.model
    def geoip_search(self, field, ip, domain=None, limit=10):
        domain = domain or []
        _logger.warn(' domain: %s' %domain)
        for f in self._geo_fields:
            if f['name'] == field:
                query_obj = self._where_calc(domain)
                self._apply_ir_rules(query_obj, 'read')
                query_obj.where_clause.append('''"%s"."%s" IS NOT NULL''' % (self._table, field))
                from_clause, where_clause, params = query_obj.get_sql()
                #~ query = "SELECT id, (%s <@> %%s) FROM %s ORDER BY %s <-> %%s LIMIT %%s" % (field, self._table, field)
                query = """with geoloc as
                            (
                            select location
                              from location l
                                   join blocks using(locid)
                             where iprange >>= %%s
                           )
                SELECT id FROM %s WHERE %s ORDER BY %s <-> (select location from geoloc) LIMIT %%s
                """ % (from_clause, where_clause, field)
                #~ params = [str(position), str(position), limit]
                params = [ip] + params + [limit]
                _logger.warn(query)
                _logger.warn(params)
                self.env.cr.execute(query, params)
                values = self.env.cr.dictfetchall()
                return [v['id'] for v in values]

    @api.model
    def geo_postal_search(self, field, country, postal_code, domain=None, distance=None, limit=10):
        # distance in degreed
        domain = domain or []
        for f in self._geo_fields:
            if f['name'] == field:
                query_obj = self._where_calc(domain)
                self._apply_ir_rules(query_obj, 'read')
                query_obj.where_clause.append('''"%s"."%s" IS NOT NULL''' % (self._table, field))
                if distance:
                    query_obj.where_clause.append('''"%s"."%s" <-> (select location from geoloc) < %%s''' % (self._table, field))
                from_clause, where_clause, params = query_obj.get_sql()
                if distance:
                    params.append(distance)
                #~ query = "SELECT id, (%s <@> %%s) FROM %s ORDER BY %s <-> %%s LIMIT %%s" % (field, self._table, field)
                query = """with geoloc as
                            (
                            select location
                              from location l
                             where country=%%s AND postalcode=%%s
                           )
                SELECT id FROM %s WHERE %s ORDER BY "%s"."%s" <-> (select location from geoloc) LIMIT %%s
                """ % (from_clause, where_clause, self._table, field)
                # ~ SELECT id FROM %s WHERE %s IS NOT NULL ORDER BY %s <-> (select location from geoloc) LIMIT %%s
                # ~ """ % (self._table, field, field)
                #~ params = [str(position), str(position), limit]
                params = [country, postal_code] + params + [limit]
                _logger.warn(query)
                _logger.warn(params)
                self.env.cr.execute(query, params)
                values = self.env.cr.dictfetchall()
                return [v['id'] for v in values]

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'postgres.geo.fields']

    _geo_fields = [{'name': 'position', 'type': 'point', 'depends': ['partner_longitude', 'partner_latitude'], 'compute': 'compute_position'}]

    @api.model
    def compute_position(self):
        return (self.partner_longitude, self.partner_latitude)


class GeoIpResolver(object):

    def record_by_addr(self, ip):
        res = None
        try:
            query = """select country, location
                          from location l
                               join blocks using(locid)
                         where iprange >>= %s"""
            request.env.cr.execute(query, [ip])
            res = request.env.cr.dictfetchone()
            if res:
                res = {
                    'ip': ip,
                    'country_code': res['country'],
                    'country_name': res['country'],
                    'longitude': eval(res['location'])[0],
                    'latitude': eval(res['location'])[1],
                }
        except:
            res = None
        return res


class ir_http(models.AbstractModel):
    _inherit = 'ir.http'

    geo_ip_resolver = GeoIpResolver()
