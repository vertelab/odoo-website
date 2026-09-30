# -*- coding: utf-8 -*-
{
    'name': 'Website: AI — Recruitment',
    'version': '18.0.1.0.1',
    'summary': 'OKF-indexering av jobbannonser (hr.job)',
    'category': 'Website',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Undermodul till website_ai. Lägger ai.okf.mixin på hr.job så att
        publicerade jobbannonser blir OKF-koncept.

        Egen modul (inte i website_ai) så att en bar website-installation
        slipper website_hr_recruitment — mönstret från okf-mixin D10.

        Annonsen har `name`, `description` och `requirements`: modellen
        sammanfattar sig själv med befattning + avdelning + plats, vilket
        är det en arbetssökande söker.
    """,
    'depends': [
        'website_ai',
        'website_hr_recruitment',
    ],
    'data': [
        'data/okf_artifact_types_hr.xml',
        'data/okf_debug_actions.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
