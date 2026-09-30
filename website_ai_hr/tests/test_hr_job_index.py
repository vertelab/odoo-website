# -*- coding: utf-8 -*-
"""Tester för website_ai_hr (okf-mixin F3.3)."""

from odoo.tests import common, tagged


@tagged('okf', 'website', 'post_install', '-at_install')
class TestHrJobIndex(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Job = cls.env['hr.job']
        cls.Mixin = cls.env['ai.okf.mixin']

    def _make_job(self, name='OKF-jobb', description='<p>Vi söker en utvecklare.</p>',
                  requirements='<p>Erfarenhet av Odoo.</p>'):
        return self.Job.create({
            'name': name,
            'description': description,
            'requirements': requirements,
        })

    def test_mixin_is_inherited(self):
        for f in ('okf_body', 'okf_summary', 'okf_tags', 'okf_dirty'):
            self.assertIn(f, self.Job._fields, f)

    def test_text_source_has_name_and_description(self):
        job = self._make_job()
        text = job._okf_body_source()
        self.assertIn('OKF-jobb', text)
        self.assertIn('utvecklare', text)
        self.assertIn('Odoo', text)
        self.assertNotIn('<p>', text)

    def test_own_summary_has_department(self):
        """Befattning + avdelning är de viktigaste orden i en annons."""
        dept = self.env['hr.department'].create({'name': 'Teknik'})
        job = self._make_job()
        job.department_id = dept
        summary = job._okf_summary_source()
        self.assertIn('OKF-jobb', summary)
        self.assertIn('Teknik', summary)

    def test_job_becomes_concept(self):
        job = self._make_job()
        concept = job._okf_index_record()
        self.assertTrue(concept)
        # Språkmedveten nyckel (D4): suffix på flerspråkig DB.
        base = 'hr.job,%s' % job.id
        self.assertTrue(
            concept.concept_key == base
            or concept.concept_key.startswith(base + ','))
        self.assertEqual(concept.artifact_type_id.name, 'job_posting')

    def test_registered_for_indexing(self):
        self.assertIn('hr.job', self.Mixin._okf_indexable_models())

    def test_artifact_type_belongs_to_bridge(self):
        atype = self.env['ai.artifact.type'].search(
            [('name', '=', 'job_posting')], limit=1)
        self.assertTrue(atype)
        self.assertEqual(atype.bridge_module, 'website_ai_hr')
