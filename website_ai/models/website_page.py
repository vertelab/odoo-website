# -*- coding: utf-8 -*-
"""website.page — OKF-indexerbar (website_ai).

Modellen äger sina KÄLLOR; `ai.okf.mixin` (ai_agent_core) äger fälten och
flaggan. Ingen domän nämns i kärnan — den här filen är den enda platsen
som vet att `website.page` finns.

Texten läses via `with_context(lang=...)` när indexeraren loopar per språk
(okf-mixin D4). `arch_db` är `xml_translate` — Odoo översätter enskilda
textnoder inuti markupen, så `with_context` ger rätt renderad helhet utan
att vi behöver känna till lagringsformatet.
"""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'ai.okf.mixin']

    # ── Källmetoder ────────────────────────────────────────────────────

    def _okf_text_source(self):
        """Sidans text ur `view_id.arch_db` — hela materialet.

        `arch_db` är `xml_translate`: jsonb per nod, inte en hel sträng.
        Att läsa via `self` (och därmed `with_context(lang=...)` när
        anroparen satt det) ger rätt språkversion utan att vi rör jsonb.
        """
        self.ensure_one()
        view = self.view_id
        if not view:
            return ''
        arch = view.arch_db or ''
        if not arch:
            return ''
        return self._okf_html_to_text(arch)

    def _okf_summary_source(self):
        """Ingen egen sammanfattning — låt kedjan avgöra.

        En webbsida har ingen `teaser` eller `subtitle`. Är texten kort
        används den som den är; är den lång tar Allmän assistent vid.
        """
        return None

    def _okf_tags_source(self):
        """Taggarna: sajtens namn + sidans URL-segment.

        URL:en är en ärlig tagg — `/om-oss` säger vad sidan handlar om,
        och den är stabil över innehållsändringar.
        """
        self.ensure_one()
        tags = []
        if self.website_id:
            tags.append(self.website_id.name)
        if self.url and self.url not in ('/', '/homepage'):
            segment = self.url.strip('/').split('/')[0]
            if segment:
                tags.append(segment)
        return tags

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        `arch_db` bor på `view_id` (via `_inherits`), men `write` på sidan
        propagerar dit — så `arch_db` fångas här. `is_published` (från
        `website.published.mixin`) styr om sidan ska indexeras alls.
        """
        return {'arch_db', 'url', 'name', 'is_published', 'website_id'}

    def _okf_skip_reason(self):
        """Opublicerad sida = "tomt just nu", inte "tomt för alltid".

        En sida kan publiceras senare. Att avföra den hade tappat den
        permanent (okf-mixin D4). Därför None — behåll flaggan.
        """
        return None

    def _okf_owner_vals(self):
        """Sajtens företag — inte `env.company`.

        En multisite-installation har flera `website`-poster med olika
        `company_id`. Konceptet ska ägas av den sajt sidan tillhör.
        """
        self.ensure_one()
        company = self.website_id.company_id or self.env.company
        return {'owner_company_id': company.id}

    # ── Hjälpare ───────────────────────────────────────────────────────

    @staticmethod
    def _okf_html_to_text(html):
        """HTML → text. Använder mixinens `_html_to_text` om den finns.

        `ai.memory.mixin` har en `_html_to_text` (HTMLParser-baserad).
        Den bor på en annan mixin, så vi kan inte ärva den härifrån —
        men vi kan använda den om modellen finns i miljön.
        """
        if not html:
            return ''
        try:
            from odoo.addons.ai_agent_core.models.ai_memory_mixin import (
                AIMemoryMixin)
            return AIMemoryMixin._html_to_text(html)
        except Exception:  # noqa: BLE001 — fallback är ett giltigt utfall
            _logger.debug('website_ai: _html_to_text saknas — använder rå text')
            return html
