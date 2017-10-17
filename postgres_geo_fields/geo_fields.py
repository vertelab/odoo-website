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
        _logger.warn('\n\n_auto_init\n\n')
        res = super(GeoFields, self)._auto_init(cr, context)
        _logger.warn('\n\n_auto_init after super\n\n')
        #~ _logger.warn('\n\n_auto_init %s\n\n' % self._select_column_data(cr))
        columns = self._select_column_data(cr)
        for field in self._geo_fields:
            _logger.warn('\n\n_auto_init %s\n\n' % field)
            if field['name'] not in columns:
                cr.execute('ALTER TABLE "%s" ADD COLUMN "%s" %s' % (self._table, field['name'], field['type']))
        _logger.warn('\n\n_auto_init before return\n\n')
    
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(GeoFields, self).create(vals)
        geo_vals = {}
        for field in self._geo_fields:
            if field.get('compute') and hasattr(self, field['compute']):
                present = False
                for dependency in field.get('depends', []):
                    if dependency in vals:
                        present = True
                    else:
                        present = False
                        break
                if present:
                    geo_vals[field['name']] = getattr(self, field['compute'])(dict([(d, vals[d]) for d in field['depends']]))
        if geo_vals:
            query = 'UPDATE "%s" SET %s WHERE id IN %%s' % (self._table, ','.join([('"%s"=%%s' % f) for f in geo_vals]))
            params = [str(geo_vals[f]) for f in geo_vals] + [tuple(res.ids)]
            self.env.cr.execute(query, params)
        return res

    @api.multi
    def write(self, vals):
        res = super(GeoFields, self).write(vals)
        geo_vals = {}
        for field in self._geo_fields:
            if field.get('compute') and hasattr(self, field['compute']):
                present = False
                for dependency in field.get('depends', []):
                    if dependency in vals:
                        present = True
                    else:
                        present = False
                        break
                if present:
                    geo_vals[field['name']] = getattr(self, field['compute'])(dict([(d, vals[d]) for d in field['depends']]))
        if geo_vals:
            query = 'UPDATE "%s" SET %s WHERE id IN %%s' % (self._table, ','.join([('"%s"=%%s' % f) for f in geo_vals]))
            params = [str(geo_vals[f]) for f in geo_vals] + [tuple(self.ids)]
            self.env.cr.execute(query, params)
        return res
    
    @api.model
    def geo_search(self, field, position, limit):
        for f in self._geo_fields:
            if f['name'] == field:
                #~ query = "SELECT id, (%s <@> %%s) FROM %s ORDER BY %s <-> %%s LIMIT %%s" % (field, self._table, field)
                query = "SELECT id FROM %s WHERE %s IS NOT NULL ORDER BY %s <-> %%s LIMIT %%s" % (self._table, field, field)
                #~ params = [str(position), str(position), limit]
                params = [str(position), limit]
                _logger.warn(query)
                _logger.warn(params)
                self.env.cr.execute(query, params)
                values = self.env.cr.dictfetchall()
                return [v['id'] for v in values]

    @api.model
    def geoip_search(self, field, ip, limit):
        for f in self._geo_fields:
            if f['name'] == field:
                #~ query = "SELECT id, (%s <@> %%s) FROM %s ORDER BY %s <-> %%s LIMIT %%s" % (field, self._table, field)
                query = """with geoloc as
                            (
                            select location
                              from location l
                                   join blocks using(locid)
                             where iprange >>= %%s
                           )
                SELECT id FROM %s WHERE %s IS NOT NULL ORDER BY %s <-> (select location from geoloc) LIMIT %%s
                """ % (self._table, field, field)
                #~ params = [str(position), str(position), limit]
                params = [ip, limit]
                _logger.warn(query)
                _logger.warn(params)
                self.env.cr.execute(query, params)
                values = self.env.cr.dictfetchall()
                return [v['id'] for v in values]
    
    @api.model
    def geo_postal_search(self, field, country, postal_code, limit):
        for f in self._geo_fields:
            if f['name'] == field:
                #~ query = "SELECT id, (%s <@> %%s) FROM %s ORDER BY %s <-> %%s LIMIT %%s" % (field, self._table, field)
                query = """with geoloc as
                            (
                            select location
                              from location l
                                   join blocks using(locid)
                             where country=%%s AND postalcode=%%s
                           )
                SELECT id FROM %s WHERE %s IS NOT NULL ORDER BY %s <-> (select location from geoloc) LIMIT %%s
                """ % (self._table, field, field)
                #~ params = [str(position), str(position), limit]
                params = [country, postal_code, limit]
                _logger.warn(query)
                _logger.warn(params)
                self.env.cr.execute(query, params)
                values = self.env.cr.dictfetchall()
                return [v['id'] for v in values]

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'postgres.geo.fields']
    
    position_x = fields.Float('Longitude')
    position_y = fields.Float('Latitude')
    
    _geo_fields = [{'name': 'position', 'type': 'point', 'depends': ['position_x', 'position_y'], 'compute': 'compute_position'}]
    
    @api.model
    def compute_position(self, vals):
        return (vals['position_y'], vals['position_x'])
