# -*- coding: utf-8 -*-
"""hr.job — OKF-indexerbar (website_ai_hr).

Undermodul till website_ai. Modellen äger sina KÄLLOR; mixinen i
ai_agent_core äger fälten och flaggan.

En jobbannons är en sökbar text: befattning, beskrivning och krav.
Modellen sammanfattar sig SJÄLV — en LLM hade formulerat om samma fakta
olika varje gång, och befattningen + platsen är de viktigaste orden.
"""

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HrJob(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job', 'ai.okf.mixin']

    # OKF-taggar: egen relationstabell (en many2many kan inte ligga
    # pa en abstrakt mixin — den ger samma tabell for alla arvande).
    okf_tags = fields.Many2many(
        'ai.okf.tag', 'hr_job_okf_tag_rel', 'res_id', 'tag_id',
        string='OKF Tags')

    # ── Källmetoder ────────────────────────────────────────────────────

    def _okf_body_source(self):
        """Annonsens text — befattning + beskrivning + krav.

        `description` och `requirements` är `html_translate`. Namnet läggs
        först: det är den mest sökbara delen.
        """
        self.ensure_one()
        parts = []
        if self.name:
            parts.append(self.name)
        for fname in ('description', 'requirements'):
            val = self[fname] if fname in self._fields else False
            if val:
                parts.append(self._okf_html_to_text(val))
        return '\n\n'.join(p for p in parts if p and p.strip())

    def _okf_summary_source(self):
        """Annonsens EGEN sammanfattning: befattning, avdelning, plats.

        Detta är vad en arbetssökande söker ("jobb i Göteborg inom
        ekonomi"), och det är deterministiskt — samma annons ger samma text.
        """
        self.ensure_one()
        bits = [self.name or '']
        if self.department_id:
            bits.append('Avdelning: %s' % self.department_id.name)
        company = self.company_id or self.env.company
        if company and company.name:
            bits.append('Plats: %s' % company.name)
        if 'job_details' in self._fields and self.job_details:
            bits.append(self._okf_html_to_text(self.job_details)[:200])
        summary = ' — '.join(b for b in bits if b)
        return summary or None

    def _okf_langs(self):
        """Översättbart innehåll — indexera per installerat språk (D4).

        En svensk version blir ett syskon-koncept, inte en ny version.
        """
        return self._okf_installed_langs()

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella."""
        return {'name', 'description', 'requirements', 'department_id',
                'company_id', 'website_published'}

    def _okf_skip_reason(self):
        """Opublicerad annons = "tomt just nu" — behåll flaggan.

        En annons som publiceras senare ska indexeras då, inte avföras
        som ett tomt legacy-minne.
        """
        return None

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12) — spårbar till website_ai_hr."""
        return 'job_posting'

    def _okf_owner_vals(self):
        """Annonsens företag — inte `env.company` (multisite)."""
        self.ensure_one()
        company = self.company_id or self.env.company
        return {'owner_company_id': company.id}

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera jobbannonsen för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell.
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('hr.job')
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
            _logger.debug('website_ai_hr: _html_to_text saknas')
            return html
