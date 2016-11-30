# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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

from openerp.addons.website_fts.html2text import html2text
import re
from collections import Counter

import logging
_logger = logging.getLogger(__name__)

# https://github.com/ekorn/Keywords/blob/master/stopwords/swedish-stopwords.txt
STOP_WORDS = ['aderton','adertonde','adjö','aldrig','alla','allas','allt','alltid','alltså','än','andra','andras','annan','annat','ännu','artonde','artonn','åtminstone','att','åtta','åttio','åttionde','åttonde','av','även','båda','bådas','bakom','bara','bäst','bättre','behöva','behövas','behövde','behövt','beslut','beslutat','beslutit','bland','blev','bli','blir','blivit','bort','borta','bra','då','dag','dagar','dagarna','dagen','där','därför','de','del','delen','dem','den','deras','dess','det','detta','dig','din','dina','dit','ditt','dock','du','efter','eftersom','elfte','eller','elva','en','enkel','enkelt','enkla','enligt','er','era','ert','ett','ettusen','få','fanns','får','fått','fem','femte','femtio','femtionde','femton','femtonde','fick','fin','finnas','finns','fjärde','fjorton','fjortonde','fler','flera','flesta','följande','för','före','förlåt','förra','första','fram','framför','från','fyra','fyrtio','fyrtionde','gå','gälla','gäller','gällt','går','gärna','gått','genast','genom','gick','gjorde','gjort','god','goda','godare','godast','gör','göra','gott','ha','hade','haft','han','hans','har','här','heller','hellre','helst','helt','henne','hennes','hit','hög','höger','högre','högst','hon','honom','hundra','hundraen','hundraett','hur','i','ibland','idag','igår','igen','imorgon','in','inför','inga','ingen','ingenting','inget','innan','inne','inom','inte','inuti','ja','jag','jämfört','kan','kanske','knappast','kom','komma','kommer','kommit','kr','kunde','kunna','kunnat','kvar','länge','längre','långsam','långsammare','långsammast','långsamt','längst','långt','lätt','lättare','lättast','legat','ligga','ligger','lika','likställd','likställda','lilla','lite','liten','litet','man','många','måste','med','mellan','men','mer','mera','mest','mig','min','mina','mindre','minst','mitt','mittemot','möjlig','möjligen','möjligt','möjligtvis','mot','mycket','någon','någonting','något','några','när','nästa','ned','nederst','nedersta','nedre','nej','ner','ni','nio','nionde','nittio','nittionde','nitton','nittonde','nödvändig','nödvändiga','nödvändigt','nödvändigtvis','nog','noll','nr','nu','nummer','och','också','ofta','oftast','olika','olikt','om','oss','över','övermorgon','överst','övre','på','rakt','rätt','redan','så','sade','säga','säger','sagt','samma','sämre','sämst','sedan','senare','senast','sent','sex','sextio','sextionde','sexton','sextonde','sig','sin','sina','sist','sista','siste','sitt','sjätte','sju','sjunde','sjuttio','sjuttionde','sjutton','sjuttonde','ska','skall','skulle','slutligen','små','smått','snart','som','stor','stora','större','störst','stort','tack','tidig','tidigare','tidigast','tidigt','till','tills','tillsammans','tio','tionde','tjugo','tjugoen','tjugoett','tjugonde','tjugotre','tjugotvå','tjungo','tolfte','tolv','tre','tredje','trettio','trettionde','tretton','trettonde','två','tvåhundra','under','upp','ur','ursäkt','ut','utan','utanför','ute','vad','vänster','vänstra','var','vår','vara','våra','varför','varifrån','varit','varken','värre','varsågod','vart','vårt','vem','vems','verkligen','vi','vid','vidare','viktig','viktigare','viktigast','viktigt','vilka','vilken','vilket','vill']
#STOP_WORDS2 = ['a','about','above','after','again','against','all','am','an','and','any','are','aren't','as','at','be','because','been','before','being','below','between','both','but','by','can't','cannot','could','couldn't','did','didn't','do','does','doesn't','doing','don't','down','during','each','e.g.','few','for','from','further','had','hadn't','has','hasn't','have','haven't','having','he','he'd','he'll','he's','her','here','here's','hers','herself','him','himself','his','how','how's','i','i'd','i'll','i'm','i've','if','in','into','is','isn't','it','it's','its','itself','let's','me','more','most','mustn't','my','myself','no','nor','not','of','off','on','once','only','or','other','ought','our','ours','ourselves','out','over','own','same','shan't','she','she'd','she'll','she's','should','shouldn't','so','some','such','than','that','that's','the','their','theirs','them','themselves','then','there','there's','these','they','they'd','they'll','they're','they've','this','those','through','to','too','under','until','up','very','was','wasn't','we','we'd','we'll','we're','we've','were','weren't','what','what's','when','when's','where','where's','which','while','who','who's','whom','why','why's','with','won't','would','wouldn't','you','you'd','you'll','you're','you've','your','yours','yourself','yourselves']

class fts_fts(models.Model):
    _name = 'fts.fts'
    _order = "name, rank, count"
    
    name = fields.Char(index=True)
    #~ res_model = fields.Many2one(comodel_name='ir.model')
    res_model = fields.Char()
    res_id    = fields.Integer()
    count = fields.Integer(default=1)
    rank = fields.Integer(default=10)
    group_ids = fields.Many2many(comodel_name="res.groups")
    
    @api.one
    @api.depends('res_model','res_id')
    def _model_record(self):
        if self.res_model and self.res_id and self.env[self.res_model].browse(self.res_id):
            self.model_record = self.env[self.res_model].browse(self.res_id)
    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].search([('state', '!=', 'manual')])
        return [(model.model, model.name) for model in models if not model.model.startswith('ir.')]    
    model_record = fields.Reference(string="Record",selection="_reference_models",compute="_model_record",store=True,index=True)
    #~ model_name = fields.Char(string="Model Name",related="model_record.name")
    #~ model_type = fields.Char(string="Model Type",related="res_model.name")

    @api.model
    def update_html(self,res_model,res_id,html='',groups=None):
        self.env['fts.fts'].search([('res_model','=',res_model),('res_id','=',res_id)]).unlink()
        #~ long_list = [w for w in re.sub(' +',' ',html2text(html.decode('utf-8')).encode('utf-8').strip().replace('\n','').lower()).split(' ') if not w in STOP_WORDS]
        long_list = re.sub(' +',' ',html2text(html.decode('utf-8')).encode('utf-8').strip().replace('\n','').lower()).split(' ')
        _logger.warn(long_list)
        for word,count in Counter(long_list).items():
            self.create({'res_model': res_model,'res_id': res_id, 'name': word,'count': count,'groups_ids': groups})
        
class view(models.Model):
    _inherit = 'ir.ui.view'

    @api.one
    @api.onchange('arch','groups_id')
    def _full_text_search_update(self):
        self.env['fts.fts'].update_html(self._name,self.id,html=self.arch,groups=self.groups_id)

#~ class WebsiteFullTextSearch(http.Controller):
    #~ _results_per_page = 10
    #~ _max_text_content_len=500
    #~ _text_segment_back=100
    #~ _text_segment_forward=300
    #~ _min_search_len=3
    #~ _search_on_pages=True
    #~ _search_on_blogposts=True
    #~ _search_on_comments=True
    #~ _search_on_customers=True
    #~ _search_on_jobs=True
    #~ _search_on_products=True
    #~ _case_sensitive=False
    #~ _search_advanced=False



    #~ def _removeSymbols(self, html_txt, symbol1, symbol2=False):

        #~ if not symbol1 and not symbol2:
            #~ return html_txt

        #~ # Function to eliminate text between: symbol1 and symbol2
        #~ index=html_txt.find(symbol1)
        #~ start=0
        #~ txt=''
        #~ while index>0:
            #~ if symbol2:
                #~ index2=html_txt.find(symbol2, index)
                #~ if index2<=0:
                    #~ break
            #~ else:
                #~ index2=index+len(symbol1)-1
            #~ txt+=html_txt[start:index]
            #~ start=index2+1
            #~ index=html_txt.find(symbol1, start)

        #~ if len(txt)==0:
            #~ return html_txt

        #~ return txt

   
 

    #~ @http.route(['/search'], type='http', auth="public", website=True)
    #~ def search_page(self, search_advanced=False, search_on_pages=True, search_on_blogposts=True, search_on_comments=True, search_on_customers=True,
                       #~ search_on_jobs=True, search_on_products=True, case_sensitive=False, search='', **post):

        #~ # Process search parameters
        #~ if isinstance(search_on_pages, unicode):
            #~ self._search_on_pages=self._normalize_bool(search_on_pages)
        #~ if isinstance(search_on_blogposts, unicode):
            #~ self._search_on_blogposts=self._normalize_bool(search_on_blogposts)
        #~ if isinstance(search_on_comments, unicode):
            #~ self._search_on_comments=self._normalize_bool(search_on_comments)
        #~ if isinstance(search_on_customers, unicode):
            #~ self._search_on_customers=self._normalize_bool(search_on_customers)
        #~ if isinstance(search_on_jobs, unicode):
            #~ self._search_on_jobs=self._normalize_bool(search_on_jobs)
        #~ if isinstance(search_on_products, unicode):
            #~ self._search_on_products=self._normalize_bool(search_on_products)
        #~ if isinstance(case_sensitive, unicode):
            #~ self._case_sensitive=self._normalize_bool(case_sensitive)
        #~ self._search_advanced=False

        #~ user = request.registry['res.users'].browse(request.cr, request.uid, request.uid, context=request.context)
        #~ values = {'user': user,
                  #~ 'is_public_user': user.id == request.website.user_id.id,
                  #~ 'header': post.get('header', dict()),
                  #~ 'searches': post.get('searches', dict()),
                  #~ 'results_count': 0,
                  #~ 'results': dict(),
                  #~ 'pager': None,
                  #~ 'search_on_pages': self._search_on_pages,
                  #~ 'search_on_blogposts': self._search_on_blogposts,
                  #~ 'search_on_comments': self._search_on_comments,
                  #~ 'search_on_customers': self._search_on_customers,
                  #~ 'search_on_jobs': self._search_on_jobs,
                  #~ 'search_on_products': self._search_on_products,
                  #~ 'case_sensitive': self._case_sensitive,
                  #~ 'search_advanced': False,
                  #~ 'sorting': False,
                  #~ 'search': search
                  #~ }

        #~ return request.website.render("website_search.search_page", values)


