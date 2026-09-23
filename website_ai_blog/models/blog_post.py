# -*- coding: utf-8 -*-
"""blog.post — OKF-indexerbar (website_ai_blog).

Undermodul till website_ai. Modellen äger sina KÄLLOR; mixinen i
ai_agent_core äger fälten och flaggan.

Skillnaden mot website.page: ett blogginlägg har `subtitle` och `teaser`.
Det betyder att modellen kan sammanfatta sig SJÄLV — ingen LLM behövs för
normala inlägg. LLM:en är fallback för riktigt långa texter.
"""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['blog.post', 'ai.okf.mixin']

    # ── Källmetoder ────────────────────────────────────────────────────

    def _okf_text_source(self):
        """Inläggets text ur `content` — hela materialet.

        `content` är `html_translate`: jsonb per nod. Att läsa via `self`
        (och därmed `with_context(lang=...)` när anroparen satt det) ger
        rätt språkversion utan att vi rör jsonb.
        """
        self.ensure_one()
        content = self.content or ''
        if not content:
            return ''
        return self._okf_html_to_text(content)

    def _okf_summary_source(self):
        """Inläggets EGEN sammanfattning — gratis och deterministisk.

        `subtitle` är författarens egen sammanfattning; `teaser` är
        ingressen. Båda är bättre än vad en LLM formulerar ur `content`,
        och de varierar inte mellan körningar.

        Returnerar None om ingen finns — då tar kedjan vid.
        """
        self.ensure_one()
        parts = []
        if self.subtitle:
            parts.append(self.subtitle.strip())
        if self.teaser_manual:
            parts.append(self._okf_html_to_text(self.teaser_manual).strip())
        if not parts:
            return None
        return ' — '.join(p for p in parts if p)

    def _okf_tags_source(self):
        """Taggarna: bloggens namn + inläggets egna taggar."""
        self.ensure_one()
        tags = []
        if self.blog_id:
            tags.append(self.blog_id.name)
        tags.extend(self.tag_ids.mapped('name'))
        return tags

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        `content` är html_translate och bor på modellen själv (till skillnad
        från website.page, där arch_db bor på view_id) — så den fångas här.
        """
        return {'name', 'subtitle', 'content', 'teaser_manual',
                'tag_ids', 'is_published', 'blog_id'}

    def _okf_skip_reason(self):
        """Opublicerat inlägg = "tomt just nu", inte "tomt för alltid"."""
        return None

    def _okf_owner_vals(self):
        """Bloggens företag — inte `env.company` (multisite)."""
        self.ensure_one()
        company = (self.website_id.company_id if self.website_id
                   else self.env.company)
        return {'owner_company_id': company.id}

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera blogginlägget för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell och kan inte påverkas av en
        ärvande brygga (mätt på luke18 2026-09-22).
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('blog.post')
        return res

    # ── Hjälpare ───────────────────────────────────────────────────────

    @staticmethod
    def _okf_html_to_text(html):
        """HTML → text via ai.memory.mixins parser (samma som website_ai)."""
        if not html:
            return ''
        try:
            from odoo.addons.ai_agent_core.models.ai_memory_mixin import (
                AIMemoryMixin)
            return AIMemoryMixin._html_to_text(html)
        except Exception:  # noqa: BLE001 — fallback är ett giltigt utfall
            _logger.debug('website_ai_blog: _html_to_text saknas')
            return html
