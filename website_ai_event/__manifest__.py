# -*- coding: utf-8 -*-
{
    'name': 'Website: AI — Event',
    'version': '18.0.1.0.0',
    'summary': 'OKF-indexering av evenemang (event.event)',
    'category': 'Website',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Undermodul till website_ai. Lägger ai.okf.mixin på event.event så
        att evenemang blir OKF-koncept.

        Egen modul (inte i website_ai) så att en bar website-installation
        slippper website_event — mönstret från okf-mixin D10.

        Evenemanget har `name` och `description`: modellen sammanfattar sig
        själv med namn + datum + plats, vilket är det en besökare söker.
    """,
    'depends': [
        'website_ai',
        'website_event',
    ],
    'data': [
        'data/okf_debug_actions.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
