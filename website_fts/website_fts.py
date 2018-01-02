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
from datetime import datetime, timedelta
import operator
import sys, traceback

#from openerp.addons.website_fts.html2text import html2text
import re
from collections import Counter

import logging
_logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except:
    _logger.info('website_fts requires bs4.')


# https://github.com/ekorn/Keywords/blob/master/stopwords/swedish-stopwords.txt
STOP_WORDS = ['aderton','adertonde','adjö','aldrig','alla','allas','allt','alltid','alltså','än','andra','andras','annan','annat','ännu','artonde','artonn','åtminstone','att','åtta','åttio','åttionde','åttonde','av','även','båda','bådas','bakom','bara','bäst','bättre','behöva','behövas','behövde','behövt','beslut','beslutat','beslutit','bland','blev','bli','blir','blivit','bort','borta','bra','då','dag','dagar','dagarna','dagen','där','därför','de','del','delen','dem','den','deras','dess','det','detta','dig','din','dina','dit','ditt','dock','du','efter','eftersom','elfte','eller','elva','en','enkel','enkelt','enkla','enligt','er','era','ert','ett','ettusen','få','fanns','får','fått','fem','femte','femtio','femtionde','femton','femtonde','fick','fin','finnas','finns','fjärde','fjorton','fjortonde','fler','flera','flesta','följande','för','före','förlåt','förra','första','fram','framför','från','fyra','fyrtio','fyrtionde','gå','gälla','gäller','gällt','går','gärna','gått','genast','genom','gick','gjorde','gjort','god','goda','godare','godast','gör','göra','gott','ha','hade','haft','han','hans','har','här','heller','hellre','helst','helt','henne','hennes','hit','hög','höger','högre','högst','hon','honom','hundra','hundraen','hundraett','hur','i','ibland','idag','igår','igen','imorgon','in','inför','inga','ingen','ingenting','inget','innan','inne','inom','inte','inuti','ja','jag','jämfört','kan','kanske','knappast','kom','komma','kommer','kommit','kr','kunde','kunna','kunnat','kvar','länge','längre','långsam','långsammare','långsammast','långsamt','längst','långt','lätt','lättare','lättast','legat','ligga','ligger','lika','likställd','likställda','lilla','lite','liten','litet','man','många','måste','med','mellan','men','mer','mera','mest','mig','min','mina','mindre','minst','mitt','mittemot','möjlig','möjligen','möjligt','möjligtvis','mot','mycket','någon','någonting','något','några','när','nästa','ned','nederst','nedersta','nedre','nej','ner','ni','nio','nionde','nittio','nittionde','nitton','nittonde','nödvändig','nödvändiga','nödvändigt','nödvändigtvis','nog','noll','nr','nu','nummer','och','också','ofta','oftast','olika','olikt','om','oss','över','övermorgon','överst','övre','på','rakt','rätt','redan','så','sade','säga','säger','sagt','samma','sämre','sämst','sedan','senare','senast','sent','sex','sextio','sextionde','sexton','sextonde','sig','sin','sina','sist','sista','siste','sitt','sjätte','sju','sjunde','sjuttio','sjuttionde','sjutton','sjuttonde','ska','skall','skulle','slutligen','små','smått','snart','som','stor','stora','större','störst','stort','tack','tidig','tidigare','tidigast','tidigt','till','tills','tillsammans','tio','tionde','tjugo','tjugoen','tjugoett','tjugonde','tjugotre','tjugotvå','tjungo','tolfte','tolv','tre','tredje','trettio','trettionde','tretton','trettonde','två','tvåhundra','under','upp','ur','ursäkt','ut','utan','utanför','ute','vad','vänster','vänstra','var','vår','vara','våra','varför','varifrån','varit','varken','värre','varsågod','vart','vårt','vem','vems','verkligen','vi','vid','vidare','viktig','viktigare','viktigast','viktigt','vilka','vilken','vilket','vill']
#STOP_WORDS2 = ['a','about','above','after','again','against','all','am','an','and','any','are','aren't','as','at','be','because','been','before','being','below','between','both','but','by','can't','cannot','could','couldn't','did','didn't','do','does','doesn't','doing','don't','down','during','each','e.g.','few','for','from','further','had','hadn't','has','hasn't','have','haven't','having','he','he'd','he'll','he's','her','here','here's','hers','herself','him','himself','his','how','how's','i','i'd','i'll','i'm','i've','if','in','into','is','isn't','it','it's','its','itself','let's','me','more','most','mustn't','my','myself','no','nor','not','of','off','on','once','only','or','other','ought','our','ours','ourselves','out','over','own','same','shan't','she','she'd','she'll','she's','should','shouldn't','so','some','such','than','that','that's','the','their','theirs','them','themselves','then','there','there's','these','they','they'd','they'll','they're','they've','this','those','through','to','too','under','until','up','very','was','wasn't','we','we'd','we'll','we're','we've','were','weren't','what','what's','when','when's','where','where's','which','while','who','who's','whom','why','why's','with','won't','would','wouldn't','you','you'd','you'll','you're','you've','your','yours','yourself','yourselves']
#~ STOP_WORDS += [' ','\n']

def cmp_len(x, y):
    if len(x) < len(y):
        return 1
    elif len(y) < len(x):
        return -1
    return 0

# TODO: Test how this method works over multiple databases
_fts_models = set()

class fts_fts(models.Model):
    _name = 'fts.fts'
    _order = "name, rank, count"

    name = fields.Char(string="Term",index=True)
    #~ res_model = fields.Many2one(comodel_name='ir.model')
    res_model = fields.Char()
    res_id = fields.Integer()
    count = fields.Integer(default=1)
    rank = fields.Integer(default=10)
    group_ids = fields.Many2many(comodel_name="res.groups")
    facet = fields.Selection([('term','Term'),('author','Author')], string='Facet')

    @api.model
    def register_fts_model(self, model):
        _fts_models.add(model)

    @api.model
    def get_fts_models(self):
        return _fts_models

    @api.model
    def update_fts_search_terms(self):
        """Update all search terms for objects marked as dirty, up to the maximum time limit. Default setting is for a cron job with a 5 minute interval."""
        _logger.info('Starting FTS update')
        count = 0
        start = datetime.now()
        limit = timedelta(minutes=float(self.env['ir.config_parameter'].get_param('website_fts.time_limit', '4.5')))
        for model in _fts_models:
            records = self.env[model].search([('fts_dirty', '=', True)], order='create_date asc')
            _logger.info('Updating FTS terms for %s(%s%s)' % (records._name, ', '.join([str(id) for id in records._ids[:10]]), ('... [%s more]' % (len(records._ids) -10)) if len(records._ids) > 10 else ''))
            for record in records:
                try:
                    record._full_text_search_update()
                    count += 1
                    # Commit to avoid locking rows for the full duration of this function.
                    self.env.cr.commit()
                except:
                    _logger.warn("Could not update FTS terms for %s" % record)
                    self.log_error('DEBUG')
                if datetime.now() - start > limit:
                    _logger.info('Time limit reached. Processed %s records. Last record to be processed was %s' % (count, record))
                    return
        _logger.info('Finished FTS update for all records')

    @api.one
    @api.depends('res_model','res_id')
    def _model_record(self):
        if self.res_model and self.res_id and self.env[self.res_model].browse(self.res_id):
            self.model_record = self.env[self.res_model].browse(self.res_id)
            #~ self.model_record = (self.res_model,self.res_id)
        else:
            self.model_record = None

    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].search([('state', '!=', 'manual')])
        return [(model.model, model.name) for model in models if (not model.model.startswith('ir.') or model.model in ['ir.attachment', 'ir.ui.view'])]
    model_record = fields.Reference(string="Record", selection="_reference_models", compute="_model_record", store=True) # ,store=True,index=True)

    @api.model
    def get_text(self, texts, words):
        text = ''
        for t in texts:
            text += ' '.join(BeautifulSoup(t, 'html.parser').findAll(text=True))
        return text

    @api.model
    def clean_punctuation(self, text):
        return text.rstrip(',').rstrip('.').rstrip(':').rstrip(';').rstrip('!')

    @api.model
    def update_html(self, res_model, res_id, html='', groups=None, facet='term', rank=10):
        self.env['fts.fts'].search([('res_model', '=', res_model), ('res_id', '=', res_id), ('facet', '=', facet)]).unlink()
        soup = BeautifulSoup(html.strip().lower(), 'html.parser') #decode('utf-8').encode('utf-8')
        texts = [self.clean_punctuation(w) for w in ' '.join([w.rstrip(',') for w in soup.findAll(text=True) if not w in STOP_WORDS + [';','=',':','(',')',' ','\n']]).split(' ')]
        for word, count in Counter(texts).items():
            if word:
                self.env['fts.fts'].create({'res_model': res_model,'res_id': res_id, 'name': '%.30s' % word.lower(),'count': count,'facet': facet,'rank': rank, 'group_ids': [(6, 0, [g.id for g in groups or []])]})

    @api.model
    def update_text(self, res_model, res_id, text='', groups=None, facet='term', rank=10):
        text = text or ''
        self.env['fts.fts'].search([('res_model', '=', res_model), ('res_id', '=', res_id), ('facet', '=', facet)]).unlink()
        text = text.strip().lower().split(' ')
        texts = [self.clean_punctuation(w) for w in ' '.join([w.rstrip(',') for w in text if not w in STOP_WORDS + [' ','\n']]).split(' ')]
        for word, count in Counter(texts).items():
            if word:
                self.env['fts.fts'].create({'res_model': res_model,'res_id': res_id, 'name': '%.30s' % word.lower(),'count': count,'facet': facet,'rank': rank, 'group_ids': [(6, 0, [g.id for g in groups or []])]})

    def word_union(self, r1, r2):
        r3 = self.env['fts.fts'].browse([])
        for r11 in r1:
            for r21 in r2:
                if r21.model_record == r11.model_record:
                    r3 |= r11
        return r3



    @api.model
    def term_search(self, search, facet=None, res_models=['product.template', 'product.product', 'blog.post'], limit=5, offset=0):
        start = datetime.now()
        word_list = []
        if '"' in search:
            for w in search.split('"'):
                if w.strip() != '':
                    word_list.append(w)
        else:
            word_list = search.split(' ')
        # Sort by longest (probably most significant) word first.
        word_list.sort(cmp_len)

# 1) get list of models for first search
# 2) search each word within the ever reduced list of models
# the model-list has to be complete, limit can only be applied at end
# TODO: save number of words found for each model_record to have an impact for rank

        word_rank = {}
        words = {}
        for w in word_list:
            domain = [
                ('name', 'like', '%%%s%%' % w),
                ('model_record', '!=', False),
                ('res_model', 'in', res_models),
                '|',
                    ('group_ids', '=', False),
                    ('group_ids', 'in', [g.id for g in self.env.user.groups_id])
            ]
            if words:
                domain.append(('model_record', 'in', words.keys()))
            _logger.debug(domain)
            # Create updated list of matching terms
            words2 = {}
            for term in self.env['fts.fts'].search_read(domain, ['model_record', 'rank']):
                if term['model_record'] in words:
                    # A match to the same record is already in the list. Compare ranks and keep the lowest match.
                    if term['rank'] < words[term['model_record']]['rank']:
                        words2[term['model_record']] = {
                            'id': term['id'],
                            'rank': term['rank'],
                        }
                    else:
                        words2[term['model_record']] = words[term['model_record']]
                else:
                    # No previous match in the list. Add this one.
                    words2[term['model_record']] = {
                        'id': term['id'],
                        'rank': term['rank'],
                    }
            # Replace the previous words with the updated version
            words = words2
            if not words:
                break
            _logger.debug(words)
        words = self.env['fts.fts'].browse([words[w]['id'] for w in words]).sorted(key=lambda r: r.rank)
        _logger.warn('words: %s' % words)


        facets = []

        for f in set(words.mapped('facet')):
            w,c = Counter(words.filtered(lambda w: w.facet == f)).items()[0]
            facets.append((w.facet,c))
        models = []
        for m in set(words.mapped('res_model')):
            w,c = Counter(words.filtered(lambda w: w.res_model == m)).items()[0]
            models.append((w.res_model,c))
        delta_t = datetime.now() - start
        _logger.info('FTS search (%s) took %.2f s' % (search, (delta_t.seconds + (delta_t.microseconds / 1000000.0))))
        return {'terms': words,'facets': facets,'models': models, 'docs': words.filtered(lambda w: w.model_record != False).mapped('model_record')[:limit]}


    @api.one
    def get_object(self,words):
        #~ _logger.warn('get_object')
        if self.res_model == 'ir.ui.view':
            page = self.env['ir.ui.view'].browse(self.res_id)
            return {'name': page.name, 'body': self.get_text([page.arch],words)}
        return {'name': '<none>', 'body': '<empty>'}

    @api.model
    def log_error(self, level='DEBUG'):
        e = sys.exc_info()
        _logger.log(getattr(logging, level), ''.join(traceback.format_exception(e[0], e[1], e[2])))

class fts_model(models.AbstractModel):
    _name = 'fts.model'
    _description = 'FTS Model'

    _fts_fields = []

    fts_dirty = fields.Boolean(string='Dirty', help='FTS terms for this record need to be updated', default=True)

    @api.model
    def _setup_complete(self):
        res = super(fts_model, self)._setup_complete()
        _logger.warn('_setup_complete %s' % self._name)
        if self._name != 'fts.model':
            self.env['fts.fts'].register_fts_model(self._name)
        return res

    @api.multi
    def _full_text_search_delete(self):
        terms = self.env['fts.fts'].search(['|' for i in range(len(self._ids) - 1)] + [('model_record', '=', '%s,%s' % (self._name, id)) for id in self._ids])
        if terms:
            terms.unlink()

    @api.one
    def _full_text_search_update(self):
        self._full_text_search_delete()
        self.fts_dirty = False

    #~ @api.model
    #~ @api.returns('self', lambda value: value.id)
    #~ def create(self, vals):
        #~ res = super(fts_model, self).create(vals)
        #~ res._full_text_search_update()
        #~ return res

    @api.multi
    def write(self, vals):
        for f in self._fts_fields:
            if f in vals:
                vals['fts_dirty'] = True
            break
        return super(fts_model, self).write(vals)

    @api.multi
    def unlink(self):
        self._full_text_search_delete()
        return super(fts_model, self).unlink()

class fts_website(models.Model):
    _name = 'fts.website'

    name = fields.Char(string="Url")
    xml_id = fields.Char()
    body = fields.Text()
    group_ids = fields.Many2many(comodel_name="res.groups")
    res_id = fields.Integer()


class view(models.Model):
    _name = 'ir.ui.view'
    _inherit = ['ir.ui.view', 'fts.model']

    _fts_fields = ['arch', 'groups_id']

    @api.one
    def _full_text_search_update(self):
        super(view, self)._full_text_search_update()
        if self.type == 'qweb' and 't-call="website.layout"' in self.arch:
            website = self.env['fts.website'].search([('res_id','=',self.id)])
            if website:
                website.write({'name': self.name, 'xml_id': self.xml_id, 'body': self.env['fts.fts'].get_text([self.arch],[]), 'res_id': self.id, 'group_ids': self.groups_id })
            else:
                website = self.env['fts.website'].create({'name': self.name, 'xml_id': self.xml_id, 'body': self.env['fts.fts'].get_text([self.arch],[]), 'res_id': self.id, 'group_ids': self.groups_id })
            self.env['fts.fts'].update_html('fts.website',website.id,html=website.body,groups=website.group_ids)

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
        vals = request.env['fts.fts'].term_search(search)
        vals['kw'] = search
        return request.website.render("website_fts.search_result", vals)

    @http.route(['/search_suggestion'], type='json', auth="public", website=True)
    def search_suggestion(self, search='', facet=None, res_model=None, limit=0, offset=0, **kw):
        result = request.env['fts.fts'].term_search(search, facet, res_model, limit, offset)
        #~ _logger.warn(result)
        result_list = result['terms']
        rl = []
        i = 0
        while i < len(result_list) and len(rl) < 5:
            r = result_list[i]
            if r.model_record._name in ['product.template', 'product.public.category']:
                rl.append({
                    'res_id': r.res_id,
                    'model_record': r.model_record._name,
                    'name': r.model_record.name,
                })
            elif r.model_record._name == 'product.product':
                rl.append({
                    'res_id': r.res_id,
                    'model_record': r.model_record._name,
                    'name': r.model_record.name,
                    'product_tmpl_id': r.model_record.product_tmpl_id.id,
                })
            elif r.model_record._name == 'blog.post':
                rl.append({
                    'res_id': r.res_id,
                    'model_record': r.model_record._name,
                    'name': r.model_record.name,
                    'blog_id': r.model_record.blog_id.id,
                })
            elif r.model_record._name == 'product.facet.line':
                rl.append({
                    'res_id': r.res_id,
                    'model_record': r.model_record._name,
                    'product_tmpl_id': r.model_record.product_tmpl_id.id,
                    'product_name': r.model_record.product_tmpl_id.name,
                })
            i += 1
        return rl

class fts_test(models.TransientModel):
    _name = 'fts.test'
    _description = 'FTS Test Wizard'

    search = fields.Char(string='Search Term')
    fts_ids = fields.Many2many(string='Search Results', comodel_name='fts.fts')
    log = fields.Html(string='Log', readonly=True, default="""<table class="table table-striped">
  <thead>
    <tr>
      <th>Time</th>
      <th>Search Term</th>
      <th># Hits</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>""")

    @api.one
    @api.onchange('search')
    def test_search(self):
        if self.search:
            start = datetime.now()
            result = self.env['fts.fts'].term_search(self.search)
            delta_t = datetime.now() - start
            _logger.warn(result)
            self.fts_ids = [(6, 0, [r.id for r in result['terms']])]
            rows = self.log.split('\n')
            self.log = '\n'.join(
                rows[:-2] + [
                    '<tr><td>%.2f s</td><td>%s</td><td>%s</td></tr>' % (
                        (delta_t.seconds + (delta_t.microseconds / 1000000.0)),
                        self.search,
                        len(self.fts_ids)
                )] + rows[-2:])
