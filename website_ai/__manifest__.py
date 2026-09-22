# -*- coding: utf-8 -*-
{
    'name': 'Website: AI',
    'version': '18.0.1.0.0',
    'summary': 'OKF-indexering av webbplatsinnehåll — website.page, blog.post, event.event',
    'category': 'Website',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Bryggmodul för OKF-indexering av webbplatsinnehåll.

        Lägger `ai.okf.mixin` på website.page, blog.post och event.event så
        att deras text blir OKF-koncept: taggar, länkar, en kopia av texten
        (okf_text) och en sammanfattning (okf_summary) som embeddas och söks.

        Modellen äger sina KÄLLOR (_okf_text_source, _okf_summary_source,
        _okf_tags_source, _okf_dirty_fields); mixinen i ai_agent_core äger
        fälten och flaggan. Ingen domän nämns i kärnan.

        Beroenden: ai_agent_core + website (alltid). blog och event är
        separata undermoduler (website_ai_blog, website_ai_event) så att en
        bar website-installation slipper dem.
    """,
    'depends': [
        'ai_agent_core',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_okf_record_views.xml',
        'data/okf_debug_actions.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
