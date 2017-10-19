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
class fts_fts(models.Model):
    _name = 'fts.fts'
    _order = "name, rank, count"

    name = fields.Char(string="Term",index=True)
    #~ res_model = fields.Many2one(comodel_name='ir.model')
    res_model = fields.Char()
    res_id    = fields.Integer()
    count = fields.Integer(default=1)
    rank = fields.Integer(default=10)
    group_ids = fields.Many2many(comodel_name="res.groups")
    facet = fields.Selection([('term','Term'),('author','Author')], string='Facet')

    @api.one
    @api.depends('res_model','res_id')
    def _model_record(self):
        if self.res_model and self.res_id and self.env[self.res_model].browse(self.res_id) and not self.res_model.startswith('ir.'):
            self.model_record = self.env[self.res_model].browse(self.res_id)
            #~ self.model_record = (self.res_model,self.res_id)
        else:
            self.model_record = None
    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].search([('state', '!=', 'manual')])
        return [(model.model, model.name) for model in models if not model.model.startswith('ir.')]
    model_record = fields.Reference(string="Record",selection="_reference_models",compute="_model_record",store=True) # ,store=True,index=True)

    @api.model
    def get_text(self,texts,words):
        #~ _logger.warn(texts)
        text = ''
        for t in texts:
            text += ' '.join(BeautifulSoup(t, 'html.parser').findAll(text=True))
        return text

    @api.model
    def update_html(self,res_model,res_id,html='',groups=None,facet='term',rank=10):
        self.env['fts.fts'].search([('res_model','=',res_model),('res_id','=',res_id),('facet','=',facet)]).unlink()
        soup = BeautifulSoup(html.strip().lower(), 'html.parser') #decode('utf-8').encode('utf-8')
        texts = [w.rstrip(',').rstrip('.').rstrip(':').rstrip(';') for w in ' '.join([w.rstrip(',') for w in soup.findAll(text=True) if not w in STOP_WORDS + [';','=',':','(',')',' ','\n']]).split(' ')]
        #~ raise Warning(Counter(texts).items())
        for word,count in Counter(texts).items():
            self.create({'res_model': res_model,'res_id': res_id, 'name': '%.30s' % word,'count': count,'facet': facet,'rank': rank}) # 'groups_ids': groups})

    @api.model
    def update_text(self,res_model,res_id,text='',groups=None,facet='term',rank=10):
        text = text or ''
        self.env['fts.fts'].search([('res_model','=',res_model),('res_id','=',res_id),('facet','=',facet)]).unlink()
        text = text.strip().lower().split(' ')
        texts = [w.rstrip(',').rstrip('.').rstrip(':').rstrip(';') for w in ' '.join([w.rstrip(',') for w in text if not w in STOP_WORDS + [' ','\n']]).split(' ')]
        #~ _logger.warn(texts)
        #~ _logger.warn(Counter(texts).items())
        for word,count in Counter(texts).items():
            self.env['fts.fts'].create({'res_model': res_model,'res_id': res_id, 'name': '%.30s' % word,'count': count,'facet': facet,'rank': rank}) # 'groups_ids': groups})

    def word_union(self, r1, r2):
        r3 = self.env['fts.fts'].browse([])
        for r11 in r1:
            for r21 in r2:
                if r21.model_record == r11.model_record:
                    r3 |= r11
        return r3

    @api.model
    def term_search(self, search, facet=None, res_model=None, limit=5, offset=0):
        word_list = []
        if '"' in search:
            for w in search.split('"'):
                if w.strip() != '':
                    word_list.append(w)
        else:
            word_list = search.split(' ')
        word_list = [w for w in word_list if w]
        query = "SELECT DISTINCT ON (model_record) id, model_record FROM fts_fts WHERE %s%s%s%s" % (
            " OR ".join(["name ILIKE %s" for w in word_list]),
            (" AND %s" % " OR ".join(["model_record LIKE %s" for m in res_model])) if res_model else '',
            " LIMIT %s" if limit else '',
            " OFFSET %s" if offset else '')
        params = ['%%%s%%' % w for w in word_list]
        for model in res_model or []:
            params.append('%s,%%' % model)
        if limit:
            params.append(limit)
        if offset:
            params.append(offset)
        _logger.debug(query)
        _logger.debug(params)
        self.env.cr.execute(query, params)
        res = self.env.cr.dictfetchall()
        _logger.debug(res)
        words = request.env['fts.fts'].browse([row['id'] for row in res])

        facets = []
        
        for f in set(words.mapped('facet')):
            w,c = Counter(words.filtered(lambda w: w.facet == f)).items()[0]
            facets.append((w.facet,c))
        models = []
        for m in set(words.mapped('res_model')):
            w,c = Counter(words.filtered(lambda w: w.res_model == m)).items()[0]
            models.append((w.res_model,c))
        return {'terms': words,'facets': facets,'models': models, 'docs': words.filtered(lambda w: w.model_record != False).mapped('model_record')[:limit]}

    @api.one
    def get_object(self,words):
        #~ _logger.warn('get_object')
        if self.res_model == 'ir.ui.view':
            page = self.env['ir.ui.view'].browse(self.res_id)
            return {'name': page.name, 'body': self.get_text([page.arch],words)}
        return {'name': '<none>', 'body': '<empty>'}


class fts_website(models.Model):
    _name = 'fts.website'

    name = fields.Char(string="Url")
    xml_id = fields.Char()
    body = fields.Text()
    group_ids = fields.Many2many(comodel_name="res.groups")
    res_id = fields.Integer()


class view(models.Model):
    _inherit = 'ir.ui.view'

    @api.one
    @api.depends('arch','groups_id')
    def _full_text_search_update(self):
        #~ _logger.warn(self.name)
        if self.type == 'qweb' and 't-call="website.layout"' in self.arch:
            website = self.env['fts.website'].search([('res_id','=',self.id)])
            if website:
                website.write({'name': self.name, 'xml_id': self.xml_id, 'body': self.env['fts.fts'].get_text([self.arch],[]), 'res_id': self.id, 'group_ids': self.groups_id })
            else:
                website = self.env['fts.website'].create({'name': self.name, 'xml_id': self.xml_id, 'body': self.env['fts.fts'].get_text([self.arch],[]), 'res_id': self.id, 'group_ids': self.groups_id })
            self.env['fts.fts'].update_html('fts.website',website.id,html=website.body,groups=website.group_ids)
        self.full_text_search_update = '' #just for depends to work
    full_text_search_update = fields.Char(compute="_full_text_search_update", store=True)


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
