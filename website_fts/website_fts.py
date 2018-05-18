# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from openerp.http import request
from openerp.exceptions import Warning
from openerp.tools import SKIPPED_ELEMENT_TYPES, SKIPPED_ELEMENTS
from datetime import datetime, timedelta
import operator
import sys, traceback
import string
from lxml import etree

#from openerp.addons.website_fts.html2text import html2text
import re
from collections import Counter

import logging
_logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except:
    _logger.info('website_fts requires bs4.')

# https://www.compose.com/articles/indexing-for-full-text-search-in-postgresql/

_fts_models = {}

class fts_model(models.AbstractModel):
    """
    Inherit this model to make a model searchable through the FTS.
    
    All inheriting models need to define the fields that should be used to build the searchable document in _get_fts_fields().
    """

    _name = 'fts.model'
    _description = 'FTS Model'

    _fts_fields = []
    _fts_fields_d = []

    def _get_fts_fields(self):
        """
        Return a list of dicts describing how to build the FTS search document.
        [{
            'name': field_name,
            ['weight': 'A' / 'B' / 'C' / 'D',]
            ['trigger_only': True / False,]
            ['sql_vars': [variable_name],]
            ['sql_select': [select_expression],]
            ['sql_vector': [vector_expression],]
            ['dependencies': [depends_field_name],]
        }]
        name: the name of the field to be used in fts.
        weight: A label for weighting search results. A > B > C > D.
        trigger_only: Only use this field to trigger recompute. Field should not be used to build the searchable document.
        sql_vars: List of extra variables to declare in the document building function.
        sql_select: List of SQL expressions to execute before building the document.
        sql_vector: List of vector expressions that should be added to the document. Use this to override the automatic handling.
        dependencies: Override field dependencies with this list. ***NOT IMPLEMENTED***
        """
        return  []

    _fts_trigger = fields.Boolean(string='Trigger FTS Update', help='Change this field to update FTS.', compute='_compute_fts_trigger', store=True)

    @api.model
    def _get_fts_depends(self):
        fields = set()
        for field in self._get_fts_fields():
            if field.get('dependencies'):
                fields |= set(field['dependencies'])
            else:
                fields.add(field['name'])
        _logger.debug('%s._get_fts_depends: %s' % (self._name, fields))
        return list(fields)

    @api.depends(_get_fts_depends)
    @api.one
    def _compute_fts_trigger(self):
        """
        Dummy field to trigger the updates on SQL level. Tracking
        changes is much easier on Odoo level than on SQL level. Make
        this field dependant on the relevant fields.
        """
        # TODO: Trigger this update when relevant translations change.
        if self._fts_trigger:
            self._fts_trigger = True
        else:
            self._fts_trigger = False

    @api.cr_context
    def _lang_o2pg(self, cr, lang, context=None):
        """
        Return the corresponding name of the language and fts column in postgresql.
        """
        col_name = '_fts_vector_%s' % lang.lower()
        return 'simple', col_name
        # Language specific search rules work very poorly when matching incomplete terms. Skip them until we find a better solution.
        #~ langs = {
            #~ 'da': 'danish',
            #~ 'nl': 'dutch',
            #~ 'en': 'english',
            #~ 'fi': 'finnish',
            #~ 'fr': 'french',
            #~ 'de': 'german',
            #~ 'hu': 'hungarian',
            #~ 'it': 'italian',
            #~ 'no': 'norwegian',
            #~ 'pt': 'portuguese',
            #~ 'ro': 'romanian',
            #~ 'ru': 'russian',
            #~ 'es': 'spanish',
            #~ 'sv': 'swedish',
            #~ 'tr': 'turkish',
        #~ }
        #~ lang = lang.split('_')[0]
        #~ return langs.get(lang, 'simple'), col_name

    @api.cr_context
    def _fts_drop_obsolete_sql_stuff(self, cr, context):
        """
        Drop obsolete SQL functions and triggers that were defined in earlier versions.
        """
        cr.execute("DROP TRIGGER IF EXISTS upd_fts_vector ON %s;" % self._table)
        func_name = '%s_fts_vector_trigger' % self._table
        cr.execute("DROP FUNCTION IF EXISTS %s();" % func_name)

    @api.cr_context
    def _fts_get_langs(self, cr, context):
        langs = set()
        cr.execute("SELECT code from res_lang WHERE id in (SELECT lang_id FROM website_lang_rel);")
        for d in cr.dictfetchall():
            langs.add(d['code'])
        return langs

    @api.cr_context
    def _get_fts_models(self, cr, context=None):
        return _fts_models[cr.dbname].copy()

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
        res = super(fts_model, self)._auto_init(cr, context)
        
        
        #~ cr.execute("SELECT res_id FROM ir_model_data WHERE module = 'base' and name = 'user_root';")
        #~ res = cr.dictfetchone()
        #~ user_id = res['res_id']
        #~ _logger.warn('\n\nuser_id: %s' % user_id)
        #~ env = api.Environment(cr, user_id, context)
        #~ env[self._name]._init_fts_fields()
        #~ return res
    
    #~ @api.model
    #~ def _init_fts_fields(self):
        #~ cr, context = self._cr, self._context
        cr.execute("DROP FUNCTION IF EXISTS website_fts_translate_term(language text, term text, model text, field text, t_name text, obj_id integer);")
        cr.execute("""CREATE FUNCTION website_fts_translate_term(language text, term text, model text, field text, t_name text, obj_id integer) RETURNS text AS $$
DECLARE result text;
    BEGIN
        result := model || ',' || field;
        SELECT value INTO result FROM ir_translation it WHERE
            it.name = result AND
            it.lang = language AND
            it.res_id = obj_id AND
            it.value != '' AND
            it.src = term
        ORDER BY id
        LIMIT 1;
        return COALESCE(result, term);
    END;
$$ LANGUAGE plpgsql;""")
        # TODO: Replace this with _fts_get_langs and test it
        langs = set()
        cr.execute("SELECT code from res_lang WHERE id in (SELECT lang_id FROM website_lang_rel);")
        for d in cr.dictfetchall():
            langs.add(d['code'])
        _logger.debug('FTS languages: %s' % ', '.join(langs))
        columns = self._select_column_data(cr)
        fts_fields = self._get_fts_fields()
        for lang in langs:
            update_index = False
            ps_lang, col_name = self._lang_o2pg(cr, lang, context)
            if self._auto and col_name not in columns:
                # Add _fts_vector column to the table
                _logger.debug('Adding column %s.%s' % (self._table, col_name))
                cr.execute('ALTER TABLE "%s" ADD COLUMN "%s" tsvector' % (self._table, col_name))
                update_index = True
            if self._auto and fts_fields and '_fts_trigger' in columns:
                self._fts_drop_obsolete_sql_stuff(cr, context)
                trigger_name = 'upd%s' % col_name
                func_name = '%s%s_trigger' % (self._table, col_name)
                
                cr.execute("DROP TRIGGER IF EXISTS %s ON %s;" % (trigger_name, self._table))
                
                # Create function that updates the new _fts_vector column.
                cr.execute("DROP FUNCTION IF EXISTS %s();" % func_name)
                # Declarations of extra variables the function needs
                declares = []
                # SQL code to select data into the variables
                selects = []
                # Code to build a part of the document
                fields = []
                var_count = 0
                # TODO: Add support for more column types (float and int)
                for field in fts_fields:
                    if field.get('trigger_only'):
                        continue
                    if '.' in field['name']:
                        # Hande related fields dot notation
                        relational_fields = field['name'].split('.')
                        field_obj = self._fields[relational_fields[0]]
                    else:
                        # Handle related fields
                        field_obj = self._fields[field['name']]
                        relational_fields = field_obj.related
                    _logger.debug('related fields: %s' % (relational_fields,))
                    if field.get('sql_vector'):
                        # TODO: Test that this actually works
                        declares += field.get('sql_vars', [])
                        selects += [s.format(lang=lang, ps_lang=ps_lang, col_name=col_name, weight=field.get('weight', 'D')) for s in field.get('sql_selects', [])]
                        fields += [f.format(lang=lang, ps_lang=ps_lang, col_name=col_name, weight=field.get('weight', 'D')) for f in field['sql_vector']]
                    elif relational_fields:
                        var_name = "fts_tmp_%s" % var_count
                        var_count += 1
                        declares.append("DECLARE %s text;" % var_name)
                        selects.append(self._fts_get_related_select(cr, var_name, lang, ps_lang, self, relational_fields, context))
                        fields.append("setweight(to_tsvector('%s', COALESCE(%s, '')), '%s')" % (
                            ps_lang, var_name, field.get('weight', 'D')))
                    elif field_obj.translate:
                        var_name = "fts_tmp_%s" % var_count
                        var_count += 1
                        declares.append("DECLARE %s text;\n" % var_name)
                        selects.append("SELECT website_fts_translate_term('%s', new.%s, '%s', '%s', '%s', new.id) INTO %s;" % (
                            lang, field['name'], self._name, field['name'], self._table, var_name))
                        fields.append("setweight(to_tsvector('%s', COALESCE(%s, '')), '%s')" % (
                            ps_lang, var_name, field.get('weight', 'D')))
                    else:
                        fields.append("setweight(to_tsvector('%s', COALESCE(new.%s, '')), '%s')" % (ps_lang, field['name'], field.get('weight', 'D')))
                fields = ' ||\n        '.join(fields) + ';'
                declares = ['\n%s' % d for d in declares]
                selects = ['\n    %s' % s for s in selects]
                expr = "CREATE FUNCTION %s() RETURNS trigger AS $$%s\n" \
                "BEGIN%s\n" \
                "    new.%s := %s\n" \
                "    return new;\n" \
                "END;\n" \
                "$$ LANGUAGE plpgsql;" % (func_name, ''.join(declares), ''.join(selects), col_name, fields)
                _logger.debug(expr)
                cr.execute(expr)
                expr = "CREATE TRIGGER %s BEFORE INSERT OR UPDATE OF _fts_trigger ON %s " \
                    "FOR EACH ROW EXECUTE PROCEDURE %s();" % (trigger_name, self._table, func_name)
                _logger.debug(expr)
                cr.execute(expr)
                if update_index:
                    # Create index on the _fts_vector column.
                    cr.execute("CREATE INDEX %s%s_idx ON %s USING GIST (%s);" % (self._table, col_name, self._table, col_name))
        return res

    @api.cr_context
    def _fts_get_related_select(self, cr, var_name, lang, ps_lang, model, fields, context):
        """
        Build the SQL statements necessary to get translated terms for a chain of relational field.
        :param lang: A string with the name of the language in Odoo.
        :param ps_lang: A string with the name of the language in postgresql.
        :param model: An Odoo model object.
        :param fields: A list of fields (strings). First item must be a relational field on model. Last item must be a text field.
        :return: TBD
        """
        _logger.debug('_fts_get_related_select model = %s, fields = %s' % (model, fields))
        env = api.Environment(cr, None, context)
        res = ''
        for field in fields:
            field_obj = model._fields[field]
            if field_obj.type == 'one2many':
                table = model._table
                model = self.pool.get(field_obj.comodel_name)
                inverse_name = field_obj.inverse_name
                if not res:
                    res = "FROM %s WHERE %s IN (SELECT id FROM %s WHERE id = new.id)" % (model._table, inverse_name, table)
                else:
                    res = "FROM %s WHERE %s IN (SELECT id %s)" % (model._table, inverse_name, res)
                #~ _logger.debug('one2many: %s' % res)
            elif field_obj.type == 'many2one':
                table = model._table
                model = self.pool.get(field_obj.comodel_name)
                if not res:
                    res = "FROM %s WHERE id IN (SELECT %s FROM %s WHERE id = new.id)" % (model._table, field, table)
                else:
                    res = "FROM %s WHERE id IN (SELECT %s %s)" % (model._table, field, res)
                #~ _logger.debug('many2one: %s' % res)
            elif field_obj.type == 'many2many':
                table = model._table
                model = self.pool.get(field_obj.comodel_name)
                relation, column1, column2 = field_obj.to_column()._sql_names(env[field_obj.model_name])
                if not res:
                    res = "FROM %s WHERE id IN (SELECT %s FROM %s WHERE %s = new.id)" % (model._table, column2, relation, column1)
                else:
                    res = "FROM %s WHERE id IN (SELECT %s FROM %s WHERE %s IN (SELECT id %s))" % (model._table, column2, relation, column1, res)
                #~ _logger.debug('many2many: %s' % res)
            else:
                if field_obj.translate:
                    res = "SELECT string_agg(name, ' ') INTO %s FROM (SELECT website_fts_translate_term('%s', obj.name, '%s', '%s', '%s', obj.id) as name FROM (SELECT id, %s %s) AS obj) AS result;" % (var_name, lang, model._name, field, model._table, field, res)
                else:
                    res = "SELECT string_agg(name, ' ') INTO %s FROM (SELECT %s %s) AS result;" % (var_name, field, res)
                #~ _logger.debug('finished: %s' % res)
        return res

    @api.model
    def _fts_etree2document(self, arch):
        """
        Convert an etree object to a list describing an FTS document.
        """
        doc = []
        if type(arch) not in SKIPPED_ELEMENT_TYPES and arch.tag not in SKIPPED_ELEMENTS:
            text = arch.text and arch.text.strip()
            if text:
                doc.append(text)
            tail = arch.tail and arch.tail.strip()
            if tail:
                doc.append(tail)

            for attr_name in ('title', 'alt', 'label', 'placeholder'):
                attr = arch.get(attr_name)
                attr = attr and attr.strip()
                if attr:
                    doc.append(attr)
            for node in arch.iterchildren("*"):
                doc += self._fts_etree2document(node)
        return doc

    @api.model
    def fts_xml2document(self, xml):
        try:
            arch_tree = etree.fromstring(xml)
        except:
            try:
                arch_tree = etree.fromstring('<div>%s</div>' % xml)
            except:
                _logger.exception("Couldn't read XML document.")
                return ''
        doc = self._fts_etree2document(arch_tree)
        return ' '.join(doc)

    @api.model
    def _fts_reindex(self, langs=None):
        """
        Reindex the FTS columns for this model.
        :param langs: List of languages that should be reindexed. Will default to all languages.
        """
        if not langs:
            langs = self._fts_get_langs()
        for lang in langs:
            expr = "REINDEX INDEX %s_fts_vector_%s_idx;" % (self._table, lang)
            _logger.debug(expr)
            self.env.cr.execute(expr)

    @api.model
    def _fts_update_vector(self, record_ids=None):
        """
        Trigger an update of the FTS columns for this model.
        :param record_ids: List of the records that should be updated. Will default to all records.
        """
        _logger.debug('Updating FTS for %s' % self._name)
        if record_ids:
            params = [tuple(record_ids)]
            where = ' AND id IN %s'
        else:
            params = []
            where = ''
        expr = "SELECT id FROM %s WHERE _fts_trigger in (false, NULL)%s;" % (self._table, where)
        _logger.debug(expr)
        self.env.cr.execute(expr, params)
        f_ids = [d['id'] for d in self.env.cr.dictfetchall()]
        expr = "SELECT id FROM %s WHERE _fts_trigger = true%s;" % (self._table, where)
        _logger.debug(expr)
        self.env.cr.execute(expr, params)
        t_ids = [d['id'] for d in self.env.cr.dictfetchall()]
        if f_ids:
            expr = "UPDATE %s SET _fts_trigger = true WHERE id in %%s;" % self._table
            _logger.debug(expr)
            _logger.debug(f_ids)
            self.env.cr.execute(expr, [tuple(f_ids)])
        if t_ids:
            expr = "UPDATE %s SET _fts_trigger = false WHERE id in %%s;" % self._table
            _logger.debug(expr)
            _logger.debug(t_ids)
            self.env.cr.execute(expr, [tuple(t_ids)])

    @api.model
    def _fts_get_ts_query(self, query, ps_lang):
        self._cr.execute("SELECT plainto_tsquery(%s, %s);", [ps_lang, query])
        query = self._cr.dictfetchone()['plainto_tsquery'].split("'")
        res = ""
        inside_str = False
        for s in query:
            if inside_str:
                res += "%s:*" % s
            else:
                res += s
            inside_str = not inside_str
        return res

    @api.model
    def fts_search(self, query, domain=[]):
        """
        Perform an FTS search.
        :param query: The raw search string.
        :param domain: An optional Odoo search domain.
        :return: a list of dicts with ids and weights ([[{'id': 1, 'ts_rank': 0.23}]).
        """
        _logger.debug('%s.fts_search domain: %s, query: %s' % (self._name, domain, query))
        lang = self._context.get('lang')
        ps_lang, col_name = self._lang_o2pg(lang)
        _logger.debug('lang: %s, ps_lang: %s, col_name: %s' % (lang, ps_lang, col_name))
        self.check_access_rights('read')
        query = self._fts_get_ts_query(query, ps_lang)
        query_obj = self._where_calc(domain)
        self._apply_ir_rules(query_obj, 'read')
        query_obj.where_clause.append('''"%s"."%s" @@ %%s''' % (self._table, col_name))
        query_obj.where_clause_params.append(query)
        from_clause, where_clause, params = query_obj.get_sql()
        params = [query] + params
        expr = '''SELECT "%s"."id", ts_rank("%s"."%s", %%s), '%s' AS model FROM %s WHERE %s ORDER BY ts_rank DESC;''' % (
            self._table, self._table, col_name, self._name, from_clause, where_clause)
        _logger.debug(expr)
        _logger.debug(params)
        self.env.cr.execute(expr, params)
        res = {}
        results = self.env.cr.dictfetchall()
        _logger.debug(results)
        return results

    @api.model
    def fts_search_browse(self, query, domain=[]):
        """
        Perform an FTS search. Returns a recordset sorted by weight.
        """
        # TODO: Fix sorting.
        res = self.fts_search(query, domain)
        return self.browse([d['id'] for d in res])

    @api.multi
    def fts_search_suggestion(self):
        """
        Return a search result for search_suggestion.
        """
        return {
            'res_id': self.id,
            'model_record': self._name,
            'name': self.name_get()[0][1],
        }

    @api.model
    def fts_search_multi(self, query, domain=None, models=None, limit=0, offset=0, domains=None):
        """
        Perform an FTS search on the given models.
        
        :param query: The search string.
        :param domain: An Odoo domain to be added to the search.
        :param models: A list of the models to search on.
        :param limit: The limit of the search.
        :param offset: The offset of the search.
        :param domains: A dict with extra domains to be added on a per model basis ({model: domain}).
        
        :return: A list of dicts containing the search results, sorted by ts_rank ({'model': model name, 'id': record id, 'ts_rank': search result weight}).
        """
        domain = domain or []
        domains = domains or {}
        models = models or self._get_fts_models()
        results = []
        for model in models:
            res = self.env[model].fts_search(query, domain=domain + domains.get(model, []))
            for d in res:
                d['model'] = model
            results += res
        results.sort(lambda x, y: (x['ts_rank'] > y['ts_rank'] and 1) or (x['ts_rank'] < y['ts_rank'] and -1) or 0, reverse=True)
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        _logger.debug('fts_search results: %s' % results)
        return results

    @api.model
    def fts_term_search(self, query, models=None, limit=25, domain=None, offset=0):
        models = models or self._get_fts_models()
        domain = domain or []
        lang = self._context.get('lang')
        ps_lang, col_name = env['fts.model']._lang_o2pg(lang)
        _logger.debug('lang: %s, ps_lang: %s, col_name: %s' % (lang, ps_lang, col_name))
        query = self._fts_get_ts_query(query, ps_lang)
        expressions = []
        parameters = []
        for model in models:
            fts_model = self.env[model]
            fts_model.check_access_rights('read')
            query_obj = fts_model._where_calc(domain)
            fts_model._apply_ir_rules(query_obj, 'read')
            query_obj.where_clause.append('''"%s"."%s" @@ %%s''' % (fts_model._table, col_name))
            query_obj.where_clause_params.append(query)
            from_clause, where_clause, params = query_obj.get_sql()
            parameters += [query] + params
            expressions.append('''(SELECT "%s"."id", ts_rank("%s"."%s", %%s), '%s' AS model FROM %s WHERE %s ORDER BY ts_rank DESC)''' % (
                fts_model._table, fts_model._table, col_name, fts_model._name, from_clause, where_clause))
        expr = ' UNION ALL '.join(expressions) + " ORDER BY ts_rank DESC, id, model LIMIT %s OFFSET %s;"
        parameters += [limit, offset]
        _logger.debug(expr)
        _logger.debug(parameters)
        self.env.cr.execute(expr, parameters)
        results = self.env.cr.dictfetchall()
        _logger.debug(results)
        return results
    
    @api.model
    def fts_term_search_browse(self, query, models=None, limit=25, domain=None, offset=0):
        results = self.fts_term_search(query, models=models, limit=limit, domain=domain, offset=offset)
        # TODO: This could probably be done more efficiently
        for res in results:
            res['object'] = self.env[res['model']].browse(res['id'])
        return results

    @api.model
    def _setup_complete(self):
        """
        Register this model as an FTS model.
        """
        res = super(fts_model, self)._setup_complete()
        if self._name != 'fts.model':
            db = self._cr.dbname
            if db not in _fts_models:
                _fts_models[db] = set()
            _fts_models[db].add(self._name)
        return res

    #~ @api.model
    #~ @api.returns('self', lambda value: value.id)
    #~ def create(self, vals):
        #~ res = super(fts_model, self).create(vals)
        #~ res._full_text_search_update()
        #~ return res

    @api.model
    def fts_get_default_suggestion_domain(self):
        """
        Return the default domain for search suggestions.
        """
        return []

class fts_website(models.Model):
    _name = 'fts.website'

    name = fields.Char(string="Url")
    xml_id = fields.Char()
    body = fields.Text()
    group_ids = fields.Many2many(comodel_name="res.groups")
    res_id = fields.Integer()


class View(models.Model):
    _name = 'ir.ui.view'
    _inherit = ['ir.ui.view', 'fts.model']

    def _get_fts_fields(self):
        return [{
            'name': 'arch',
            'weight': 'A',
            'sql_vector': ["setweight(to_tsvector('{ps_lang}', COALESCE(arch_doc, '')), '{weight}')"],
            'sql_selects': ["SELECT document INTO arch_doc FROM ir_ui_view_fts WHERE view_id = new.id AND lang = '{lang}';"],
            'sql_vars': ['DECLARE arch_doc text;'],
        }]

    @api.model
    def _fts_update_vector(self, record_ids=None):
        """
        Update FTS columns for views.
        Search only makes sense for primary qweb views, so we limit key parts of this function to those views.
        """
        # Delete all existing ir.ui.view.fts lines. Also delete any lines belonging to non-primary or non-qweb views.
        if record_ids:
            fts_docs = self.env['ir.ui.view.fts'].sudo().search(['|', ('view_id', 'in', record_ids), '|', ('view_id.type', '!=', 'qweb'), ('view_id.mode', '!=', 'primary')])
        else:
            fts_docs = self.env['ir.ui.view.fts'].sudo().search([])
        if fts_docs:
            fts_docs.unlink()
        if record_ids:
            # Find all primary qweb views associated with the given views
            ids = set(v['id'] for v in self.env['ir.ui.view'].search_read([('id', 'in', record_ids), ('type', '=', 'qweb'), ('mode', '!=', 'primary')], ['id']))
            primary = set(v['id'] for v in self.env['ir.ui.view'].search_read([('id', 'in', record_ids), ('type', '=', 'qweb'), ('mode', '=', 'primary')], ['id']))
            while ids:
                primary |= set(v['id'] for v in self.env['ir.ui.view'].search_read([('inherit_children_ids', 'in', list(ids)), ('type', '=', 'qweb'), ('mode', '=', 'primary')], ['id']))
                ids = set(v['id'] for v in self.env['ir.ui.view'].search_read([('inherit_children_ids', 'in', list(ids)), ('type', '=', 'qweb'), ('mode', '!=', 'primary')], ['id']))
        else:
            # Find all primary qweb views
            primary = [v['id'] for v in self.env['ir.ui.view'].search_read([('mode', '=', 'primary'), ('type', '=', 'qweb')], ['id'])]
        langs = self._fts_get_langs()
        # Create ir.ui.view.fts lines for the primary views
        for id in primary:
            for lang in langs:
                arch = self.with_context(lang=lang).read_template(id)
                doc = self.fts_xml2document(arch)
                self.env['ir.ui.view.fts'].sudo().create({'document': doc, 'lang': lang, 'view_id': id})
        if record_ids:
            # Update FTS columns for both the specified views and their associated primaries
            record_ids = list(set(record_ids) | primary)
        return super(View, self)._fts_update_vector(record_ids=record_ids)

class ViewFTS(models.Model):
    _name = 'ir.ui.view.fts'

    document = fields.Char(default='')
    view_id = fields.Many2one(comodel_name='ir.ui.view', required=True, ondelete='cascade')
    lang = fields.Char(required=True)

class IrTranslation(models.Model):
    _inherit = "ir.translation"

    @api.model
    def _fts_update_records(self, records):
        for model in records:
            ids = list(records[model])
            if model == 'website':
                model = 'ir.ui.view'
            self.env[model]._fts_update_vector(record_ids=ids)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        fts_models = self.env['fts.model']._get_fts_models()
        fts_models.add('website')
        fts = {}
        res = super(IrTranslation, self).create(vals)
        for trans in res:
            model = trans.name.split(',')[0]
            if model in fts_models:
                if model not in fts:
                    fts[model] = set()
                fts[model].add(trans.res_id)
        self._fts_update_records(fts)
        return res

    @api.multi
    def unlink(self):
        fts_models = self.env['fts.model']._get_fts_models()
        fts_models.add('website')
        fts = {}
        for trans in self:
            model = trans.name.split(',')[0]
            if model in fts_models:
                if model not in fts:
                    fts[model] = set()
                fts[model].add(trans.res_id)
        res = super(IrTranslation, self).unlink()
        self._fts_update_records(fts)
        return res

    @api.multi
    def write(self, vals):
        #~ _logger.warn('%s.write(%s)' % (self, vals))
        fts_models = self.env['fts.model']._get_fts_models()
        fts_models.add('website')
        fts = {}
        for trans in self:
            model = trans.name.split(',')[0]
            if model in fts_models:
                if model not in fts:
                    fts[model] = set()
                fts[model].add(trans.res_id)
        res = super(IrTranslation, self).write(vals)
        for trans in self:
            model = trans.name.split(',')[0]
            if model in fts_models:
                if model not in fts:
                    fts[model] = set()
                fts[model].add(trans.res_id)
        self._fts_update_records(fts)
        return res

class WebsiteFullTextSearch(http.Controller):

    @http.route(['/search'], type='http', auth="public", website=True)
    def search_page(self, search_advanced=False, search_on_pages=True, search_on_blogposts=True, search_on_comments=True, search_on_customers=True,
                       search_on_jobs=True, search_on_products=True, case_sensitive=False, search='', **post):
        #~ _logger.warn(isinstance(search_on_pages, unicode))
        # Process search parameters
        if isinstance(search_on_pages, unicode):
            self._search_on_pages=self._normalize_bool(search_on_pages)
        if isinstance(search_on_blogposts, unicode):
            self._search_on_blogposts=self._normalize_bool(search_on_blogposts)
        if isinstance(search_on_comments, unicode):
            self._search_on_comments=self._normalize_bool(search_on_comments)
        if isinstance(search_on_customers, unicode):
            self._search_on_customers=self._normalize_bool(search_on_customers)
        if isinstance(search_on_jobs, unicode):
            self._search_on_jobs=self._normalize_bool(search_on_jobs)
        if isinstance(search_on_products, unicode):
            self._search_on_products=self._normalize_bool(search_on_products)
        if isinstance(case_sensitive, unicode):
            self._case_sensitive=self._normalize_bool(case_sensitive)
        self._search_advanced=False

        user = request.registry['res.users'].browse(request.cr, request.uid, request.uid, context=request.context)
        values = {'user': user,
                  'is_public_user': user.id == request.website.user_id.id,
                  'header': post.get('header', dict()),
                  'searches': post.get('searches', dict()),
                  'results_count': 0,
                  'results': dict(),
                  'pager': None,
                  'search_on_pages': self._search_on_pages,
                  'search_on_blogposts': self._search_on_blogposts,
                  'search_on_comments': self._search_on_comments,
                  'search_on_customers': self._search_on_customers,
                  'search_on_jobs': self._search_on_jobs,
                  'search_on_products': self._search_on_products,
                  'case_sensitive': self._case_sensitive,
                  'search_advanced': False,
                  'sorting': False,
                  'search': search
                  }
        #~ _logger.warn(values)
        return request.website.render("website_fts.search_page", values)

    @http.route(['/search_results'], type='http', auth="public", website=True)
    def search_result(self, search='', times=0, **post):
        terms = request.env['fts.model'].fts_term_search_browse(search)
        vals = {'terms': terms, 'kw': search}
        return request.website.render("website_fts.search_result", vals)

    @http.route(['/search_suggestion'], type='json', auth="public", website=True)
    def search_suggestion(self, search='', facet=None, res_model=None, limit=5, offset=0, **kw):
        # Get model specific search domains.
        domains = {}
        for model in res_model:
            domains[model] = request.env[model].fts_get_default_suggestion_domain()
        result = request.env['fts.model'].fts_search_multi(search, [], res_model, limit, offset, domains)
        result_models = {}
        for model in request.env['fts.model']._get_fts_models():
            ids = []
            for res in result:
                if res['model'] == model:
                    ids.append(res['id'])
            if ids:
                result_models[model] = request.env[model].browse(ids)
        result_list = []
        for record in result:
            result_list.append(result_models[record['model']].filtered(lambda r: r.id == record['id']))
        rl = []
        i = 0
        while i < len(result_list) and len(rl) < limit: 
            res = result_list[i].fts_search_suggestion()
            if res:
                rl.append(res)
            i += 1
        return rl

class fts_test_model(models.Model):
    _name = 'fts.test.model'
    _description = 'FTS Test Wizard Models'

    name = fields.Char(string='Name')

class fts_test(models.TransientModel):
    _name = 'fts.test'
    _description = 'FTS Test Wizard'

    @api.model
    def _default_fts_model_ids(self):
        for model in self.env['fts.model']._get_fts_models():
            obj = self.env['fts.test.model'].search([('name', '=', model)])
            if not obj:
                self.env['fts.test.model'].create({'name': model})

    search = fields.Char(string='Search Term')
    fts_model_ids = fields.Many2many(comodel_name='fts.test.model', string='Models', default=_default_fts_model_ids)
    user_id = fields.Many2one(string='User', comodel_name='res.users')
    log = fields.Html(string='Log', readonly=True, default="""<table class="table table-striped">
  <thead>
    <tr>
      <th>Time</th>
      <th>Search Term</th>
      <th>Models</th>
      <th># Hits</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>""")
    results = fields.Html(string='Search Results', readonly=True, default="""<table class="table table-striped">
  <thead>
    <tr>
      <th>Rank</th>
      <th>Search Term</th>
      <th>Name</th>
      <th>Model</th>
      <th>Id</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>""")

    @api.one
    @api.onchange('search', 'fts_model_ids')
    def test_search(self):
        if self.search:
            start = datetime.now()
            count = 0
            rows = self.results.split('\n')
            self.results = '\n'.join(
                rows[:11] + rows[-2:])
            for model in self.fts_model_ids:
                if self.user_id:
                    result = self.env[model.name].sudo(self.user_id.id).fts_search_browse(self.search)
                else:
                    result = self.env[model.name].fts_search_browse(self.search)
                count += len(result)
                rows = self.results.split('\n')
                self.results = '\n'.join(
                    rows[:-2] + [
                        ('    <tr><td>N/A</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                            self.search, r.name, r._model, r.id
                    )) for r in result] + rows[-2:])
                    
            delta_t = datetime.now() - start
            rows = self.log.split('\n')
            self.log = '\n'.join(
                rows[:-2] + [
                    '    <tr><td>%.2f s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                        (delta_t.seconds + (delta_t.microseconds / 1000000.0)),
                        self.search,
                        ', '.join([m.name for m in self.fts_model_ids]),
                        count
                )] + rows[-2:])

    @api.model
    def _fts_get_ts_query(self, query, ps_lang):
        self._cr.execute("SELECT plainto_tsquery(%s, %s);", [ps_lang, query])
        query = self._cr.dictfetchone()['plainto_tsquery'].split("'")
        res = ""
        inside_str = False
        for s in query:
            if inside_str:
                res += "%s:*" % s
            else:
                res += s
            inside_str = not inside_str
        return res
        
