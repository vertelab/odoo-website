# -*- coding: utf-8 -*-
"""event.event — OKF-indexerbar (website_ai_event).

Undermodul till website_ai. Modellen äger sina KÄLLOR; mixinen i
ai_agent_core äger fälten och flaggan.

Ett evenemang är tidsbundet: det som gör det sökbart är namn, datum och
plats. Modellen sammanfattar sig därför SJÄLV — en LLM hade formulerat om
samma fakta olika varje gång, och datumet är det viktigaste ordet.
"""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _name = 'event.event'
    _inherit = ['event.event', 'ai.okf.mixin']

    # ── Källmetoder ────────────────────────────────────────────────────

    def _okf_body_source(self):
        """Evenemangets text — namn + beskrivning.

        `description` är `html_translate`. Namnet läggs först: det är den
        mest sökbara delen, och beskrivningen kan vara tom.
        """
        self.ensure_one()
        parts = []
        if self.name:
            parts.append(self.name)
        if self.description:
            parts.append(self._okf_html_to_text(self.description))
        return '\n\n'.join(p for p in parts if p and p.strip())

    def _okf_summary_source(self):
        """Evenemangets EGEN sammanfattning: namn, datum, plats.

        Detta är vad en besökare söker ("vad händer i Göteborg i oktober"),
        och det är deterministiskt — samma evenemang ger samma text.
        """
        self.ensure_one()
        bits = [self.name or '']
        if self.date_begin:
            bits.append('Datum: %s' % self.date_begin.strftime('%Y-%m-%d'))
        if self.date_end and self.date_end != self.date_begin:
            bits.append('till %s' % self.date_end.strftime('%Y-%m-%d'))
        if self.address_id:
            bits.append('Plats: %s' % self.address_id.display_name)
        elif self.event_type_id:
            bits.append('Typ: %s' % self.event_type_id.name)
        summary = ' — '.join(b for b in bits if b)
        return summary or None

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella."""
        return {'name', 'description', 'date_begin', 'date_end',
                'address_id', 'event_type_id', 'tag_ids', 'is_published'}

    def _okf_skip_reason(self):
        """Opublicerat evenemang = "tomt just nu"."""
        return None

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12) — spårbar till website_ai_event."""
        return 'event'

    def _okf_owner_vals(self):
        """Evenemangets företag — inte `env.company` (multisite)."""
        self.ensure_one()
        company = self.company_id or self.env.company
        return {'owner_company_id': company.id}

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera evenemanget för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell (mätt på luke18 2026-09-22).
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('event.event')
        return res

    # ── Hjälpare ───────────────────────────────────────────────────────

    @staticmethod
    def _okf_html_to_text(html):
        """HTML → text via ai.memory.mixins parser."""
        if not html:
            return ''
        try:
            from odoo.addons.ai_agent_core.models.ai_memory_mixin import (
                AIMemoryMixin)
            return AIMemoryMixin._html_to_text(html)
        except Exception:  # noqa: BLE001
            _logger.debug('website_ai_event: _html_to_text saknas')
            return html
