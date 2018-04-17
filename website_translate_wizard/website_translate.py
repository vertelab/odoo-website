# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2018 Vertel AB (<http://vertel.se>).
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
from openerp.exceptions import Warning
from openerp.tools import ustr, SKIPPED_ELEMENT_TYPES, SKIPPED_ELEMENTS
from datetime import datetime, timedelta
import sys, traceback
from lxml import etree
from difflib import get_close_matches

import logging
_logger = logging.getLogger(__name__)

class WebsiteTranslateWizard(models.TransientModel):
    _name = 'website.translate.wizard'
    _description = 'Website Translation'
    _order = 'write_date desc'

    @api.model
    def _default_lang(self):
        selection = self.fields_get(['lang'], attributes=['selection'])['lang']['selection']
        return selection and selection[0] or None
    
    @api.model
    def _default_user_id(self):
        _logger.warn(self.env.uid)
        return self.env.uid

    name = fields.Char(related='view_id.name')
    view_id = fields.Many2one(comodel_name='ir.ui.view', string='View', domain=[('type', '=', 'qweb')], required=True, ondelete="cascade")
    view_ids = fields.Many2many(comodel_name='ir.ui.view', string='Views', compute='_get_view_ids')
    user_id = fields.Many2one(comodel_name='res.users', string='User', required=True, ondelete="cascade", default=_default_user_id)
    lang = fields.Selection(selection='_get_lang_selection', required=True, default=_default_lang)
    #~ primary = fields.Boolean(string='Primary')
    delete_unused = fields.Boolean(string='Delete Unused Translations', help="Checking this will delete all unused translations tied to this view and language.")
    translation_ids = fields.Many2many(comodel_name='ir.translation', string='Translation Terms')
    unused_translation_ids = fields.Many2many(comodel_name='ir.translation', compute='_get_unused_translation_ids', string='Unused Translation Terms')
    row_ids = fields.One2many(comodel_name='website.translate.row', string='Rows', inverse_name='wizard_id')

    @api.model
    def _get_lang_selection(self):
        langs = set()
        for website in self.env['website'].search([]):
            for lang in website.language_ids:
                if lang != website.default_lang_id:
                    langs.add((lang.code, lang.name))
        return list(langs)

    @api.depends('translation_ids', 'row_ids.translation_id')
    @api.one
    def _get_unused_translation_ids(self):
        self.unused_translation_ids = self.translation_ids - self.row_ids.mapped('translation_id')

    @api.depends('view_id')
    def _get_view_ids(self):
        self.view_ids = self.env['ir.ui.view'].search([('id', 'child_of', self.view_id and self.view_id.id or 0)])

    @api.onchange('view_id', 'lang')
    def match_translations(self):
        self._get_view_ids()
        self.row_ids = self.env['website.translate.row'].browse()
        if not (self.view_id and self.lang):
            return
        for view in self.view_ids:
            try:
                arch_tree = etree.fromstring(view.arch)
            except:
                try:
                    arch_tree = etree.fromstring('<div>%s</div>' % view.arch)
                except:
                    raise Warning("Couldn't read view %s" % view.name)
            self.translation_ids = self.env['ir.translation'].search([
                ('lang', '=', self.lang),
                ('res_id', '=', view.id),
                ('type', '=', 'view'),
                ('name', '=', 'website')])
            def translate_func(term):
                trans = self.translation_ids.filtered(lambda t: t.src == term)
                return trans
            terms = self._get_translated_terms(arch_tree, translate_func)
            missing = []
            for term in terms:
                if terms[term]:
                    trans = terms[term]
                    self.row_ids = [(6, 0, [r.id for r in self.row_ids]), (0, 0, {
                        'source': term,
                        'translated': True,
                        'multiple': len(trans) > 1,
                        'translation_id': trans[0].id,
                        'translation_ids': [(6, 0, [t.id for t in trans])],
                        'view_id': view.id,
                        'lang': self.lang,
                    })]
                else:
                    missing.append(term)
            terms = self.unused_translation_ids.mapped('source')
            _logger.warn(terms)
            for term in missing:
                trans = None
                matches = get_close_matches(term, terms, 10)
                _logger.warn('matching terms: %s' % matches)
                trans = matches and self.translation_ids.filtered(lambda t: t.source in matches[0]) or None
                translations = self.translation_ids.filtered(lambda t: t.source in matches)
                self.row_ids = [(6, 0, [r.id for r in self.row_ids]), (0, 0, {
                    'source': term,
                    'translated': False,
                    'multiple': trans and len(trans) > 1 or False,
                    'translation_id': trans and trans[0].id,
                    'translation_ids': [(6, 0, [t.id for t in translations])],
                    'view_id': view.id,
                    'lang': self.lang,
                })]

    @api.model
    def _get_translated_terms(self, arch, translate_func):
        """Search an XML tree for all translatable terms and find their corresponding translation objects.
        :param arch: etree object with the qweb arch.
        :param translate_func: A function to find translations for terms.
        :returns: A dict with translatable terms and their corresponding translation objects."""
        terms = {}

        def get_term(text):
            # Convert a text to a translation term
            if not text or not text.strip():
                return None
            text = text.strip()
            if len(text) < 2 or (text.startswith('<!') and text.endswith('>')):
                return None
            return text

        def check_trans(text):
            # Check for translations for a term and add them to the terms dict
            if term in terms:
                terms[term] |= translate_func(term)
            else:
                terms[term] = translate_func(term)

        # Run through all nodes and check for translatable terms
        if type(arch) not in SKIPPED_ELEMENT_TYPES and arch.tag not in SKIPPED_ELEMENTS:
            term = get_term(arch.text)
            if term:
                check_trans(term)
            term = get_term(arch.tail)
            if term:
                check_trans(term)
            for attr_name in ('title', 'alt', 'label', 'placeholder'): 
                term = get_term(arch.get(attr_name))
                if term:
                    check_trans(term)
            # Iterate over child nodes and add the results to terms
            for node in arch.iterchildren("*"):
                res = self._get_translated_terms(node, translate_func)
                for term in res:
                    if term in terms:
                        terms[term] |= res[term]
                    else:
                        terms[term] = res[term]
        return terms

    @api.multi
    def save_translations(self):
        # TODO: Deal with duplicate translation_id on the rows. status?
        _logger.warn('\n\n%s\n\n' % self.row_ids)
        for row in self.row_ids:
            if row.translation_id and row.translation_id.source != row.source:
                #~ _logger.warn('row.source: |%s|\nrow.translation_id.source: |%s|' % (row.source, row.translation_id.source))
                row.translation_id.write({'source': row.source})
            if self.delete_unused and self.unused_translation_ids:
                self.unused_translation_ids.unlink()

class WebsiteTranslateRow(models.TransientModel):
    _name = 'website.translate.row'
    _order = 'translated, multiple'

    @api.model
    def _default_lang(self):
        selection = self.fields_get(['lang'], attributes=['selection'])['lang']['selection']
        return selection and selection[0] or None

    source = fields.Text(string='Source')
    translated = fields.Boolean(string='Translated', default=False, help="The sources for this translation term match exactly.")
    multiple = fields.Boolean(string='Multiple Translations', default=False)
    value = fields.Text(related='translation_id.value')
    wizard_id = fields.Many2one(comodel_name='website.translate.wizard', ondelete="cascade")
    view_id = fields.Many2one(comodel_name='ir.ui.view', string='View', required=True, ondelete="cascade")
    lang = fields.Selection(selection='_get_lang_selection', required=True, default=_default_lang)
    translation_id = fields.Many2one(comodel_name='ir.translation', ondelete="cascade")
    translation_ids = fields.Many2many(comodel_name='ir.translation', string='Possible Matches')

    @api.model
    def _get_lang_selection(self):
        langs = set()
        for website in self.env['website'].search([]):
            for lang in website.language_ids:
                if lang != website.default_lang_id:
                    langs.add((lang.code, lang.name))
        return list(langs)

class IrTranslation(models.Model):
    _inherit = "ir.translation"
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if 'translation_wizard_ir_translation_ids' in self._context:
            expr = self._context.get('translation_wizard_ir_translation_ids', [])
            ids = expr and expr[0] and expr[0][2]
            if ids:
                args = list(args or [])
                args.append(('id', 'in', ids))
            names = super(IrTranslation, self).name_search(name=name, args=args, operator=operator, limit=limit)
            _logger.warn(names)
            res = []
            for trans in self.search_read([('id', 'in', [n[0] for n in names])], ['value']):
                res.append((trans['id'], trans['value']))
            return res
        return super(IrTranslation, self).name_search(name=name, args=args, operator=operator, limit=limit)

