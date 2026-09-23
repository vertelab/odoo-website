# -*- coding: utf-8 -*-
"""Tester för website_ai_blog (okf-mixin F5.1).

Bevisar att ett blogginlägg blir ett OKF-koncept — och att modellen
sammanfattar sig SJÄLV (subtitle + teaser) utan LLM.
"""

from odoo.tests import common, tagged


@tagged('okf', 'website', 'post_install', '-at_install')
class TestBlogPostIndex(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Post = cls.env['blog.post']
        cls.Mixin = cls.env['ai.okf.mixin']
        cls.blog = cls.env['blog.blog'].create({'name': 'Testbloggen'})

    def _make_post(self, name='OKF-inlägg', subtitle='En kort ingress',
                   content='<p>Brödtext om Vertel och Odoo.</p>',
                   teaser='Teaser-text'):
        return self.Post.create({
            'name': name,
            'subtitle': subtitle,
            'content': content,
            'teaser_manual': teaser,
            'blog_id': self.blog.id,
        })

    def test_mixin_is_inherited(self):
        for f in ('okf_text', 'okf_summary', 'okf_tags', 'okf_dirty'):
            self.assertIn(f, self.Post._fields, f)

    def test_text_source_reads_content(self):
        post = self._make_post()
        text = post._okf_text_source()
        self.assertIn('Vertel', text)
        self.assertNotIn('<p>', text, 'HTML ska vara strippad')

    def test_own_summary_uses_subtitle(self):
        """Modellen sammanfattar sig själv — ingen LLM behövs."""
        post = self._make_post(subtitle='Min ingress',
                               teaser='Min teaser')
        summary = post._okf_summary_source()
        self.assertIn('Min ingress', summary)
        self.assertIn('Min teaser', summary)

    def test_no_summary_without_subtitle_and_teaser(self):
        post = self._make_post(subtitle=False, teaser=False)
        self.assertIsNone(post._okf_summary_source())

    def test_tags_from_blog_and_post(self):
        tag = self.env['blog.tag'].create({'name': 'nyheter'})
        post = self._make_post()
        post.tag_ids = [(4, tag.id)]
        tags = post._okf_tags_source()
        self.assertIn('Testbloggen', tags)
        self.assertIn('nyheter', tags)

    def test_post_becomes_concept(self):
        post = self._make_post()
        concept = post._okf_index_record()
        self.assertTrue(concept)
        self.assertEqual(concept.concept_key, 'blog.post,%s' % post.id)
        self.assertEqual(concept.artifact_type_id.name, 'knowledge')

    def test_summary_comes_from_model_not_llm(self):
        """Sammanfattningen ska vara modellens egen, inte LLM:ens."""
        post = self._make_post(subtitle='Egen ingress')
        concept = post._okf_index_record()
        self.assertIn('Egen ingress', concept.summary)

    def test_registered_for_indexing(self):
        """F5.9: bryggan ska ha registrerat modellen (D11)."""
        self.assertIn('blog.post', self.Mixin._okf_indexable_models())

    def test_edit_gives_new_version(self):
        post = self._make_post()
        v1 = post._okf_index_record()
        post.write({'content': '<p>Helt ny text.</p>'})
        post.invalidate_recordset(['okf_dirty'])
        self.assertTrue(post.okf_dirty, 'redigering ska flagga')
        v2 = post._okf_index_record()
        self.assertEqual(v2.version, 2)
        self.assertEqual(v2.supersedes_id, v1)

    def test_debug_action_is_bound(self):
        action = self.env.ref('website_ai_blog.action_okf_blog_post',
                              raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.binding_model_id.model, 'blog.post')
