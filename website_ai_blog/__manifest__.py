# -*- coding: utf-8 -*-
{
    'name': 'Website: AI — Blog',
    'version': '18.0.1.0.0',
    'summary': 'OKF-indexering av blogginlägg (blog.post)',
    'category': 'Website',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Undermodul till website_ai. Lägger ai.okf.mixin på blog.post så att
        blogginlägg blir OKF-koncept.

        Egen modul (inte i website_ai) så att en bar website-installation
        slipper website_blog — mönstret från okf-mixin D10.

        Blogginlägget har redan `subtitle` och `teaser`: modellen
        sammanfattar sig SJÄLV och LLM:en behövs bara för långa texter.
    """,
    'depends': [
        'website_ai',
        'website_blog',
    ],
    'data': [
        'data/okf_debug_actions.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
