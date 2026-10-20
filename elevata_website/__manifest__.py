{
    'name': 'Elevata Website',
    # Version ledger: 18.0.1.0.0 — ported from Elevata 17.0.1.0.0.
    # Imperative arch_db patching replaced by declarative XML inheritance
    # (views/demo_content.xml).
    'version': '18.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Elevata Hiss AB publika webbplats — tema, sidor och menyer',
    'author': 'Elevata, Vertel Sverige AB',
    'maintainer': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-website/elevata_website',
    'repository': 'https://github.com/vertelab/odoo-website',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_hr_recruitment',
    ],
    'data': [
        'views/footer_cleanup.xml',
        'data/seed.xml',
        # demo_content.xml must load after seed.xml: it inherits views that
        # seed.xml creates (contactus, contactus_thanks, header_text_element).
        'views/demo_content.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'elevata_website/static/src/scss/elevata_theme.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
}
