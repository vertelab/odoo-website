# -*- coding: utf-8 -*-
"""Tester för website_ai_event (okf-mixin F5.1)."""

from datetime import datetime, timedelta

from odoo.tests import common, tagged


@tagged('okf', 'website', 'post_install', '-at_install')
class TestEventIndex(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Event = cls.env['event.event']
        cls.Mixin = cls.env['ai.okf.mixin']

    def _make_event(self, name='OKF-evenemang',
                    description='<p>En dag om Odoo och AI.</p>'):
        return self.Event.create({
            'name': name,
            'description': description,
            'date_begin': datetime.now() + timedelta(days=30),
            'date_end': datetime.now() + timedelta(days=31),
        })

    def test_mixin_is_inherited(self):
        for f in ('okf_text', 'okf_summary', 'okf_tags', 'okf_dirty'):
            self.assertIn(f, self.Event._fields, f)

    def test_text_source_has_name_and_description(self):
        event = self._make_event()
        text = event._okf_text_source()
        self.assertIn('OKF-evenemang', text)
        self.assertIn('Odoo och AI', text)
        self.assertNotIn('<p>', text)

    def test_own_summary_has_date(self):
        """Datumet är det viktigaste ordet i ett evenemang."""
        event = self._make_event()
        summary = event._okf_summary_source()
        self.assertIn('OKF-evenemang', summary)
        self.assertIn('Datum:', summary)
        self.assertIn(event.date_begin.strftime('%Y-%m-%d'), summary)

    def test_event_becomes_concept(self):
        event = self._make_event()
        concept = event._okf_index_record()
        self.assertTrue(concept)
        self.assertEqual(concept.concept_key, 'event.event,%s' % event.id)
        self.assertEqual(concept.artifact_type_id.name, 'event')

    def test_summary_comes_from_model(self):
        event = self._make_event()
        concept = event._okf_index_record()
        self.assertIn('Datum:', concept.summary)

    def test_registered_for_indexing(self):
        self.assertIn('event.event', self.Mixin._okf_indexable_models())

    def test_edit_gives_new_version(self):
        event = self._make_event()
        v1 = event._okf_index_record()
        event.write({'description': '<p>Ändrat innehåll.</p>'})
        event.invalidate_recordset(['okf_dirty'])
        self.assertTrue(event.okf_dirty)
        v2 = event._okf_index_record()
        self.assertEqual(v2.version, 2)
        self.assertEqual(v2.supersedes_id, v1)

    def test_debug_action_is_bound(self):
        action = self.env.ref('website_ai_event.action_okf_event_event',
                              raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.binding_model_id.model, 'event.event')
