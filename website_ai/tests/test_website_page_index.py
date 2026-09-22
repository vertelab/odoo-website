# -*- coding: utf-8 -*-
"""Tester för website_ai (okf-mixin F5.1, F5.7, F5.8).

Bevisar att en webbsida blir ett OKF-koncept via mixinen — och att
domänen stannar i bryggan: artefakttypen är generisk (`knowledge`),
källan bär domänen (`website.page,<id>`).
"""

from odoo.tests import common, tagged


@tagged('okf', 'website', 'post_install', '-at_install')
class TestWebsitePageIndex(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Page = cls.env['website.page']
        cls.Concept = cls.env['ai.okf.concept']
        cls.Mixin = cls.env['ai.okf.mixin']
        cls.website = cls.env['website'].search([], limit=1)
        if not cls.website:
            cls.website = cls.env['website'].create({'name': 'Test'})

    def _make_page(self, name='OKF Test', url='/okf-test',
                   arch='<div><p>Vertel är ett IT-konsultbolag i Sverige.</p></div>'):
        view = self.env['ir.ui.view'].create({
            'name': 'okf.test.view',
            'type': 'qweb',
            'arch_db': arch,
            'website_id': self.website.id,
        })
        return self.Page.create({
            'name': name,
            'url': url,
            'view_id': view.id,
            'website_id': self.website.id,
        })

    # ── Mixinen är på modellen ─────────────────────────────────────────

    def test_mixin_is_inherited(self):
        for f in ('okf_text', 'okf_summary', 'okf_tags', 'okf_links',
                  'okf_dirty', 'okf_indexed_at'):
            self.assertIn(f, self.Page._fields, f)

    def test_new_page_is_dirty(self):
        self.assertTrue(self._make_page().okf_dirty)

    # ── Källmetoderna ──────────────────────────────────────────────────

    def test_text_source_reads_arch_db(self):
        page = self._make_page()
        text = page._okf_text_source()
        self.assertIn('IT-konsultbolag', text)
        self.assertNotIn('<p>', text, 'HTML ska vara strippad')

    def test_no_own_summary(self):
        """En webbsida har ingen egen sammanfattning — kedjan avgör."""
        self.assertIsNone(self._make_page()._okf_summary_source())

    def test_tags_from_website_and_url(self):
        page = self._make_page(url='/om-oss')
        tags = page._okf_tags_source()
        self.assertIn(self.website.name, tags)
        self.assertIn('om-oss', tags)

    def test_dirty_fields_cover_content(self):
        """`arch_db` fångas av ir.ui.view-hooken, inte av sidans fältlista.

        `_inherits` delegerar bara LÄSNING — ett `view_id.write()` går genom
        `ir.ui.view`s write(). Därför står `arch_db` INTE i sidans
        `_okf_dirty_fields()`, och testet kontrollerar båda halvorna.
        """
        fields = self._make_page()._okf_dirty_fields()
        self.assertNotIn('arch_db', fields,
                         'arch_db bor på view_id — fångas av IrUiView.write')
        self.assertIn('is_published', fields)
        self.assertIn('url', fields)

    def test_view_edit_flags_page(self):
        """Redigering av arch_db ska flagga sidan (via IrUiView-hooken)."""
        page = self._make_page()
        page._okf_index_record()
        page.invalidate_recordset(['okf_dirty'])
        self.assertFalse(page.okf_dirty)
        page.view_id.write({
            'arch_db': '<div><p>Ny text i vyn.</p></div>',
        })
        page.invalidate_recordset(['okf_dirty'])
        self.assertTrue(page.okf_dirty,
                        'view_id.write(arch_db) ska flagga sidan')

    def test_owner_is_website_company(self):
        """Sajtens företag — inte env.company (multisite)."""
        page = self._make_page()
        vals = page._okf_owner_vals()
        self.assertEqual(vals['owner_company_id'], self.website.company_id.id)

    # ── Indexering ─────────────────────────────────────────────────────

    def test_page_becomes_concept(self):
        page = self._make_page()
        concept = page._okf_index_record()
        self.assertTrue(concept, 'sidan ska bli ett koncept')
        self.assertEqual(concept.concept_key, 'website.page,%s' % page.id)
        self.assertEqual(concept.source_ref, 'website.page,%s' % page.id)

    def test_artifact_type_is_generic(self):
        """F5.8: ingen domänspecifik artefakttyp — domänen bor i source_ref."""
        page = self._make_page()
        concept = page._okf_index_record()
        self.assertEqual(concept.artifact_type_id.name, 'knowledge')

    def test_no_domain_artifact_types_created(self):
        self._make_page()._okf_index_record()
        for name in ('website', 'blog_post', 'event', 'job_posting',
                     'crm_lead'):
            found = self.env['ai.artifact.type'].search(
                [('name', '=', name)], limit=1)
            if found:
                self.assertEqual(
                    found.bridge_module, 'ai_agent_core',
                    'artefakttypen %r ska inte skapas av website_ai' % name)

    def test_flag_cleared_after_index(self):
        page = self._make_page()
        page._okf_index_record()
        page.invalidate_recordset(['okf_dirty', 'okf_indexed_at'])
        self.assertFalse(page.okf_dirty)
        self.assertTrue(page.okf_indexed_at)

    def test_source_text_is_stored(self):
        """D5: källan sparas så versionsbeslutet kan jämföra den."""
        page = self._make_page()
        concept = page._okf_index_record()
        self.assertTrue(concept.source_text)
        self.assertIn('IT-konsultbolag', concept.source_text)

    def test_edit_gives_new_version(self):
        page = self._make_page()
        v1 = page._okf_index_record()
        page.view_id.write({
            'arch_db': '<div><p>Vertel är ett IT-konsultbolag i Göteborg.</p></div>',
        })
        page.invalidate_recordset(['okf_dirty'])
        self.assertTrue(page.okf_dirty, 'redigering ska flagga')
        v2 = page._okf_index_record()
        self.assertEqual(v2.version, 2)
        self.assertEqual(v2.supersedes_id, v1)

    def test_unchanged_source_gives_no_new_version(self):
        page = self._make_page()
        v1 = page._okf_index_record()
        v2 = page._okf_index_record()
        self.assertEqual(v1.id, v2.id, 'oförändrad källa = ingen ny version')

    def test_cron_covers_website_page(self):
        """F4.2: cronen hittar webbplatsmodellen via den utökningsbara listan."""
        page = self._make_page()
        self.assertIn('website.page', self.Mixin._okf_indexable_models(),
                      'bryggan ska ha registrerat modellen')
        total = self.Mixin._okf_cron_index_dirty(batch_size=20)
        self.assertGreaterEqual(total, 1)
        page.invalidate_recordset(['okf_dirty'])
        self.assertFalse(page.okf_dirty)

    def test_debug_action_is_bound(self):
        """F5.9: OKF-valet finns i skalbaggen för website.page."""
        action = self.env.ref('website_ai.action_okf_website_page',
                              raise_if_not_found=False)
        self.assertTrue(action, 'debug-åtgärden ska finnas')
        self.assertEqual(action.binding_model_id.model, 'website.page')
        no_one = self.env.ref('base.group_no_one')
        self.assertIn(no_one, action.groups_id,
                      'åtgärden ska bara synas i debug-läget')
