# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Seeds the Elevata website: pages, menus, homepage, footer, site settings.

Demo-content replacements (contact page, thank-you page, job sidebar,
header contact block, language selector, CTA button) are NOT done here.
They live in views/demo_content.xml as ordinary inherited templates, so
they are versioned, translatable and revertible like any other view.
"""

from odoo import api, models

IMG = '/elevata_website/static/src/img'


def _wrap(body):
    """Wrap page body in the standard website layout + editable structure."""
    return (
        '<div id="wrap" class="oe_structure oe_empty">'
        + body +
        '</div>'
    )


def _hero(title, subtitle, img, small=False):
    cls = 'elevata-hero' if not small else 'elevata-hero elevata-hero-sm'
    style = f"background-image: url('{IMG}/{img}');" + \
            ("min-height: 38vh;" if small else "")
    return f'''
<section class="{cls}" style="{style}">
    <div class="elevata-hero-overlay">
        <div class="container">
            <h1 class="display-4 fw-bold mb-3">{title}</h1>
            <p class="lead fs-4 mb-0">{subtitle}</p>
        </div>
    </div>
</section>'''


def _cta():
    return '''
<section class="elevata-section-dark text-center">
    <div class="container">
        <h2 class="mb-3">Behöver du hjälp med hissen?</h2>
        <p class="lead mb-4">Kontakta oss — vi återkommer så snart som möjligt.</p>
        <a href="/contactus" class="btn btn-lg btn-light">Kontakta oss</a>
    </div>
</section>'''


HOMEPAGE = _wrap(f'''
<section class="elevata-hero" style="background-image: url('{IMG}/hiss_kabin.jpg');">
    <div class="elevata-hero-overlay">
        <div class="container py-5">
            <h1 class="display-3 fw-bold mb-3">Välkommen till Elevata Hiss AB</h1>
            <p class="fs-3 mb-2" style="color:#cfd8e3;">Din Hisspartner</p>
            <p class="lead mb-4" style="max-width: 640px;">
                Med över 20 års erfarenhet inom hissbranschen erbjuder vi service,
                reparationer och modernisering — med personligt engagemang och
                helhetsansvar.
            </p>
            <a href="/contactus" class="btn btn-elevata btn-lg me-2">Kontakta oss</a>
            <a href="/service-underhall" class="btn btn-outline-light btn-lg">Våra tjänster</a>
        </div>
    </div>
</section>

<section class="elevata-section-light">
    <div class="container">
        <p class="lead text-center mb-5" style="max-width: 760px; margin: 0 auto;">
            Hos oss kan du räkna med ett engagerat och personligt bemötande från
            kunniga medarbetare. Det är viktigt för oss att ha en levande dialog
            med våra kunder såväl vid underhåll som vid reparationer och
            installationer. Därför har du alltid en personlig kontakt som tar
            ansvar och lyssnar på dig. Alla kunder är lika viktiga för oss —
            stora som små.
        </p>
        <div class="row g-4">
            <div class="col-md-6 col-lg-3">
                <div class="elevata-card text-center h-100">
                    <div class="elevata-value-icon"><i class="fa fa-wrench">&#xfeff;</i></div>
                    <h3 class="fs-5">Service &amp; Underhåll</h3>
                    <p class="text-muted mb-3">Löpande skötsel och serviceavtal för alla hissar — oavsett tillverkare.</p>
                    <a href="/service-underhall" class="btn btn-sm btn-outline-primary">Läs mer</a>
                </div>
            </div>
            <div class="col-md-6 col-lg-3">
                <div class="elevata-card text-center h-100">
                    <div class="elevata-value-icon"><i class="fa fa-gears">&#xfeff;</i></div>
                    <h3 class="fs-5">Reparationer</h3>
                    <p class="text-muted mb-3">Prisvärt alternativ för alla typer av reparationer.</p>
                    <a href="/reparationer" class="btn btn-sm btn-outline-primary">Läs mer</a>
                </div>
            </div>
            <div class="col-md-6 col-lg-3">
                <div class="elevata-card text-center h-100">
                    <div class="elevata-value-icon"><i class="fa fa-arrow-up">&#xfeff;</i></div>
                    <h3 class="fs-5">Modernisering</h3>
                    <p class="text-muted mb-3">Förläng hissens livslängd med öppna, olåsta system.</p>
                    <a href="/modernisering" class="btn btn-sm btn-outline-primary">Läs mer</a>
                </div>
            </div>
            <div class="col-md-6 col-lg-3">
                <div class="elevata-card text-center h-100">
                    <div class="elevata-value-icon"><i class="fa fa-building">&#xfeff;</i></div>
                    <h3 class="fs-5">Nyinstallation</h3>
                    <p class="text-muted mb-3">Hisslösningar för nya och befintliga fastigheter.</p>
                    <a href="/nyinstallation" class="btn btn-sm btn-outline-primary">Läs mer</a>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="elevata-section-dark">
    <div class="container text-center">
        <h2 class="mb-3">Våra värderingar</h2>
        <p class="lead mb-5" style="color:#cfd8e3;">
            Vårt fokus är alltid en långsiktig nöjd kund — genom proaktiv service
            av hög kvalitet, både på material och arbete.
        </p>
        <div class="row g-4">
            <div class="col-6 col-lg-3">
                <i class="fa fa-thumbs-up fa-2x mb-3">&#xfeff;</i>
                <h3 class="fs-6">God Service</h3>
            </div>
            <div class="col-6 col-lg-3">
                <i class="fa fa-certificate fa-2x mb-3">&#xfeff;</i>
                <h3 class="fs-6">Hög Standard</h3>
            </div>
            <div class="col-6 col-lg-3">
                <i class="fa fa-users fa-2x mb-3">&#xfeff;</i>
                <h3 class="fs-6">Professionellt Team</h3>
            </div>
            <div class="col-6 col-lg-3">
                <i class="fa fa-lightbulb-o fa-2x mb-3">&#xfeff;</i>
                <h3 class="fs-6">Kreativa Lösningar</h3>
            </div>
        </div>
    </div>
</section>
''' + _cta())


PAGE_SERVICE = _wrap(
    _hero('Service &amp; Underhåll', 'Skötsel, serviceavtal och besiktning — för alla hissar.', 'hero_bil.jpg', small=True)
    + '''
<section class="elevata-section-light">
    <div class="container" style="max-width: 860px;">
        <h2 class="mb-4">Service &amp; Underhåll</h2>
        <p>
            Skötsel och underhåll ska ske löpande efter att hissen tagits i drift.
            Vid detta kontrolleras hissens funktioner enligt hissens
            skötselinstruktion. I skötsel ingår typiskt städning, smörjning och
            justering. Skötseln ska ske fortlöpande — man kan inte vänta med att
            kalla på ett skötselföretag tills hissen gått sönder.
        </p>
        <h3 class="mt-5 mb-3">Serviceavtal</h3>
        <p>
            Med ett serviceavtal med Elevata kan du vara trygg i att vi alltid kan
            hjälpa dig. Tack vare vår stora bredd och erfarenhet kan vi utföra
            service på alla hissar, oavsett tillverkare, hisstyp och årsmodell.
            Våra servicetekniker finns på fältet för att snabbt kunna vara på
            plats. De har erfarenhet och en bred teknisk kompetens — dessutom är
            de engagerade och trevliga.
        </p>
        <p>
            Vi hjälper dig gärna med att teckna ett serviceavtal som passar just
            dig. <a href="/contactus">Kontakta oss</a> redan idag så får du hjälp.
        </p>
        <h3 class="mt-5 mb-3">Besiktning</h3>
        <p>
            Fastighetsägaren ansvarar för att en årlig besiktning av hissen
            genomförs av ett oberoende ackrediterat besiktningsorgan.
            Besiktningsmannen kontrollerar att alla säkerhetsanordningar fungerar
            på rätt sätt och säkerställer att hissen fått tillfredsställande
            skötsel.
        </p>
        <p>
            Den årliga besiktningen befriar dock inte fastighetsägaren från
            ansvar. Det är du som fastighetsägare som har ansvaret för att hissen
            hålls i gott skick och sköts på ett riktigt sätt. Skulle hissen börja
            fungera dåligt är det ditt ansvar att den stängs av.
        </p>
    </div>
</section>''' + _cta())


PAGE_REPARATIONER = _wrap(
    _hero('Reparationer', 'Prisvärd åtgärd när hissen behöver mer än service.', 'tekniker.jpg', small=True)
    + '''
<section class="elevata-section-light">
    <div class="container" style="max-width: 860px;">
        <h2 class="mb-4">Reparationer av hissar</h2>
        <p>
            Ibland händer det tyvärr att hissar behöver genomgå större
            reparationer — kanske att något upptäckts i samband med ett
            servicebesök eller på grund av en anmärkning från en besiktning.
        </p>
        <p>
            Vi erbjuder ett prisvärt alternativ för alla typer av reparationer,
            och vi tror att våra priser tål att jämföras även om ni inte är
            tidigare kund hos oss.
        </p>
        <p>
            <em>Du vet väl att du kan ta in kostnadsförslag på reparationer från
            andra aktörer än din avtalspartner om du har ett vanligt avtal?</em>
        </p>
        <a href="/contactus" class="btn btn-elevata mt-3">Begär kostnadsförslag</a>
    </div>
</section>''' + _cta())


PAGE_MODERNISERING = _wrap(
    _hero('Modernisering', 'Förläng hissens livslängd — med öppna system.', 'hiss_gammal.jpg', small=True)
    + '''
<section class="elevata-section-light">
    <div class="container" style="max-width: 860px;">
        <h2 class="mb-4">Modernisering av hissar</h2>
        <p>
            Hissen är något som få tänker på när den fungerar. En trasig eller
            dåligt fungerande hiss kan däremot ge upphov till mycket irritation
            och även konkreta problem med tillgängligheten, då många människor
            idag är helt eller delvis beroende av hiss. Liksom andra delar av en
            fastighet — ventilationssystem, tvättstuga och värmesystem — har även
            hissar en livslängd. Det är därför viktigt att budgetera och planera
            för att på sikt modernisera hissen, något som inte ingår i vanlig
            skötsel och underhåll.
        </p>
        <p>
            Om hissen i din fastighet närmar sig 20–25 år är det dags att i samråd
            med ditt hissföretag eller en konsult göra en bedömning av hissens
            status samt upprätta en plan med lämpliga åtgärder.
        </p>
    </div>
</section>
<section class="py-5">
    <div class="container">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="elevata-card h-100">
                    <h3 class="fs-5 mb-3">Flexibla och öppna styrsystem</h3>
                    <p class="text-muted mb-0">
                        Vi arbetar med olåsta hissystem med komponenter från den
                        öppna marknaden och fullt tillgänglig dokumentation. Det
                        gör underhållet enklare och mindre kostsamt, och det är
                        lättare att få tag i utbyteskomponenter med kortare
                        leveranstid.
                    </p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="elevata-card h-100">
                    <h3 class="fs-5 mb-3">Korg</h3>
                    <p class="text-muted mb-0">
                        Att renovera korginredning och sätta in ny korgdörr gör
                        att hissen ser som ny ut igen.
                    </p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="elevata-card h-100">
                    <h3 class="fs-5 mb-3">Schaktdörrar</h3>
                    <p class="text-muted mb-0">
                        Schaktdörrarna är nog det som orsakar mest driftstopp.
                        Nya eller renoverade gör underverk.
                    </p>
                </div>
            </div>
        </div>
    </div>
</section>''' + _cta())


PAGE_NYINSTALLATION = _wrap(
    _hero('Nyinstallation', 'Hisslösningar för nya och befintliga fastigheter.', 'hiss_schakt.jpg', small=True)
    + '''
<section class="elevata-section-light">
    <div class="container" style="max-width: 860px;">
        <h2 class="mb-4">Nyinstallation av hiss</h2>
        <p>
            Oavsett om det gäller en nybyggd fastighet eller en hissmontage i ett
            befintligt hus hjälper vi dig genom hela processen — från
            behovsanalys och offert till färdig installation och driftsättning.
        </p>
        <p>
            Vi arbetar med olåsta hissystem och komponenter från den öppna
            marknaden, vilket ger dig frihet att välja servicepartner även i
            framtiden — och enklare, mer prisvärt underhåll under hissens hela
            livslängd.
        </p>
        <a href="/contactus" class="btn btn-elevata mt-3">Kontakta oss för offert</a>
    </div>
</section>''' + _cta())


PAGE_OM_OSS = _wrap(
    _hero('Om Elevata', 'Personligt engagemang och helhetsansvar.', 'hiss2.jpg', small=True)
    + '''
<section class="elevata-section-light">
    <div class="container" style="max-width: 860px;">
        <h2 class="mb-4">Om oss</h2>
        <p>
            Med kontor och lager mitt i mellan Göteborg och Varberg erbjuder vi
            service och underhåll, reparationer samt modernisering av alla på
            marknaden förekommande hissar.
        </p>
        <p>
            Elevata bygger på över 20 års erfarenhet från hissbranschen. Efter
            lång tid som underentreprenör driver vi nu verksamheten i egen regi —
            med samma engagemang, men med helhetsansvar direkt mot våra kunder.
        </p>
        <p>
            Hos oss får du alltid en personlig kontakt som tar ansvar och lyssnar
            på dig. Vi tror på en levande dialog med våra kunder — vid underhåll,
            reparationer och installationer.
        </p>
    </div>
</section>''' + _cta())


PAGE_POLICY = _wrap(
    _hero('Integritetspolicy', 'Behandling av personuppgifter på Elevata Hiss AB.', 'hiss.jpg', small=True)
    + '''
<section class="elevata-section-light">
    <div class="container" style="max-width: 860px;">
        <h2 class="mb-4">Integritetspolicy</h2>
        <p class="text-muted">Behandling av personuppgifter på Elevata Hiss AB</p>
        <p>För Elevata Hiss AB är personlig integritet viktig. Vi eftersträvar en hög nivå av dataskydd. I denna policy förklarar vi hur vi samlar in och använder personuppgifter. Vi beskriver också dina rättigheter och hur du kan göra dem gällande.</p>
        <p>Du är alltid välkommen att kontakta oss om du har frågor om hur vi behandlar dina personuppgifter. Kontaktuppgifter står sist i denna text.</p>

        <h3 class="mt-4">Vad är en personuppgift och vad är en behandling av personuppgifter?</h3>
        <p>Personuppgifter är alla uppgifter om en levande fysisk person som direkt eller indirekt kan kopplas till den personen. Det handlar inte bara om namn och personnummer utan även om till exempel bilder och e-postadresser.</p>
        <p>Behandling av personuppgifter är allt som sker med personuppgifterna i IT-systemen, oavsett om det handlar om mobila enheter eller datorer. Det handlar om till exempel insamling, registrering, strukturering, lagring, bearbetning och överföring. I vissa fall kan även manuella register omfattas.</p>

        <h3 class="mt-4">Personuppgiftsansvarig</h3>
        <p>För de behandlingar som sker inom Elevata Hiss AB:s verksamhet är Elevata Hiss AB personuppgiftsansvarig. (Org.nr: 556757-6870, Almedalsvägen 147, 43963 Frillesås).</p>

        <h3 class="mt-4">Vilka personuppgifter samlar vi in om dig och varför?</h3>
        <p>Vi behandlar i huvudsak ditt namn, personnummer, adress och kontaktuppgifter, bankkonto för löneutbetalning samt uppgifter som du gett om närmast anhörig.</p>
        <p>Vi behandlar dina personuppgifter för att kunna fullgöra våra skyldigheter enligt vårt anställningsavtal med dig och för att uppfylla regler i lag och kollektivavtal.</p>

        <h3 class="mt-4">Personuppgiftsbiträden</h3>
        <p>I en del situationer är det nödvändigt för oss att anlita andra parter, till exempel IT-leverantörer för HR-system eller elektroniska körjournaler. De är då personuppgiftsbiträden till oss. Vi kontrollerar personuppgiftsbiträden för att säkerställa att de garanterar säkerheten och sekretessen för personuppgifterna. När personuppgiftsbiträden anlitas sker det bara för de ändamål som är förenliga med de ändamål vi själva har för behandlingen.</p>

        <h3 class="mt-4">Aktörer som är självständigt personuppgiftsansvariga</h3>
        <p>Vi delar även dina personuppgifter med vissa andra aktörer som är självständigt personuppgiftsansvariga, till exempel myndigheter som Skatteverket, när vi är skyldiga att lämna ut sådana uppgifter med stöd av lag eller myndighetsbeslut. När dina personuppgifter delas med en aktör som är självständigt personuppgiftsansvarig gäller den organisationens integritetspolicy och personuppgiftshantering.</p>

        <h3 class="mt-4">Hur länge sparar vi dina personuppgifter?</h3>
        <p>Vi sparar aldrig dina personuppgifter längre än vad som är nödvändigt för respektive ändamål. Vissa uppgifter i bokföringen behöver på grund av lagstiftning till exempel sparas minst sju år.</p>

        <h3 class="mt-4">Vad är dina rättigheter som registrerad?</h3>
        <p>Som registrerad har du enligt gällande lagstiftning ett antal rättigheter. Du har rätt till att få ett utdrag som visar vilka personuppgifter vi har registrerade om dig. Du kan begära rättelse av felaktiga uppgifter och i vissa fall radering.</p>

        <h3 class="mt-4">Kontakta oss vid frågor om hur vi behandlar personuppgifter</h3>
        <p>Om du har frågor om hur vi behandlar personuppgifter kontakta <span t-esc="res_company.email"/> som är ansvarig för personuppgiftsfrågor.</p>
        <p>Vi kan komma att göra ändringar i vår integritetspolicy. Den senaste versionen av integritetspolicyn finns alltid här på webbplatsen.</p>
    </div>
</section>''')


FOOTER = '''
<div class="container py-5">
    <div class="row">
        <div class="col-md-5 mb-4">
            <img t-att-src="'/web/image/website/%d/logo' % website.id"
                 style="max-height: 56px;" class="mb-3" t-att-alt="res_company.name"/>
            <p style="color:#cfd8e3;">
                Med kontor och lager mitt i mellan Göteborg och Varberg erbjuder
                vi service och underhåll, reparationer samt modernisering av alla
                på marknaden förekommande hissar.
            </p>
        </div>
        <div class="col-md-3 mb-4">
            <h5>Kontakta oss</h5>
            <p class="mb-1">
                <a t-att-href="'mailto:' + (res_company.email or '')"
                   style="color:#cfd8e3;" t-esc="res_company.email"/><br/>
                <a t-att-href="'tel:' + (res_company.phone or '')"
                   style="color:#cfd8e3;" t-esc="res_company.phone"/>
            </p>
        </div>
        <div class="col-md-4 mb-4">
            <h5 t-esc="res_company.name"/>
            <p class="mb-0" style="color:#cfd8e3;">
                <span t-esc="res_company.street"/><br/>
                <span t-esc="res_company.zip"/> <span t-esc="res_company.city"/><br/>
                <span t-esc="res_company.country_id.name"/>
            </p>
        </div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.15);"/>
    <p class="text-center mb-0" style="color:#8fa3b8;">
        Copyright © <t t-esc="res_company.name"/>
    </p>
</div>
'''


class ElevataWebsiteSeed(models.AbstractModel):
    _name = 'elevata.website.seed'
    _description = 'Seed Elevata website content'

    PAGES = [
        ('service-underhall', 'Service & Underhåll', PAGE_SERVICE, 20),
        ('reparationer', 'Reparationer', PAGE_REPARATIONER, 25),
        ('modernisering', 'Modernisering', PAGE_MODERNISERING, 30),
        ('nyinstallation', 'Nyinstallation', PAGE_NYINSTALLATION, 35),
        ('om-oss', 'Om Elevata', PAGE_OM_OSS, 40),
    ]

    @api.model
    def seed(self):
        """Seed the parts of the site that cannot be expressed as data.

        The demo-content replacements (contact page, thank-you page, job
        sidebar, header contact block, language selector, CTA button) live
        in views/demo_content.xml as ordinary inherited templates. Only the
        content this module owns is created here.
        """
        site = self.env['website'].get_current_website()
        site.name = 'Elevata'
        self._seed_logo(site)
        self._seed_company()
        self._seed_pages(site)
        self._seed_homepage(site)
        self._seed_footer(site)
        self._seed_menus(site)
        return True

    def _seed_logo(self, site):
        """Set the dark Elevata logo as the website logo + favicon."""
        import base64

        from odoo.tools import misc
        with misc.file_open(
                'elevata_website/static/src/img/elevata_logo_dark.png',
                'rb') as f:
            site.logo = base64.b64encode(f.read())
        with misc.file_open(
                'elevata_website/static/src/img/elevata_icon.png',
                'rb') as f:
            site.favicon = base64.b64encode(f.read())

    def _seed_company(self):
        """Fill in Elevata company details so the website shows correct
        contact info immediately after install."""
        company = self.env['res.company'].browse(1)
        company.write({
            'name': 'Elevata Hiss AB',
            'street': 'Varbergsvägen 2090',
            'zip': '439 61',
            'city': 'Frillesås',
            'country_id': self.env.ref('base.se').id,
            'phone': '010-20 40 305',
            'email': 'info@elevata.se',
            'website': 'https://www.elevata.se',
            'vat': 'SE556757687001',
        })

    def _view_for(self, name, body, website=None):
        key = 'elevata_website.page_%s' % name.replace('-', '_')
        view = self.env['ir.ui.view'].search([
            ('key', '=', key),
            ('website_id', 'in', [website.id, False] if website else [False]),
        ], limit=1)
        arch = (
            '<t t-name="%s"><t t-call="website.layout">%s</t></t>'
            % (key, body)
        )
        vals = {
            'name': key,
            'key': key,
            'type': 'qweb',
            'arch': arch,
            'website_id': website.id if website else False,
        }
        if view:
            view.write({'arch': arch})
        else:
            view = self.env['ir.ui.view'].create(vals)
        return view

    def _seed_pages(self, site):
        Page = self.env['website.page']
        for url, title, body, _seq in self.PAGES:
            view = self._view_for(url, body, website=site)
            page = Page.search([
                ('url', '=', '/' + url),
                ('website_id', '=', site.id),
            ], limit=1)
            vals = {
                'name': title,
                'url': '/' + url,
                'view_id': view.id,
                'website_id': site.id,
                'is_published': True,
                'website_indexed': True,
            }
            if page:
                page.write(vals)
            else:
                Page.create(vals)

        # Integritetspolicy under Övrigt (ingen toppmeny direkt)
        view = self._view_for('integritetspolicy', PAGE_POLICY, website=site)
        if not Page.search([('url', '=', '/integritetspolicy'),
                            ('website_id', '=', site.id)]):
            Page.create({
                'name': 'Integritetspolicy',
                'url': '/integritetspolicy',
                'view_id': view.id,
                'website_id': site.id,
                'is_published': True,
                'website_indexed': True,
            })

    def _seed_homepage(self, site):
        """Replace the homepage body.

        Odoo ships a global homepage page (website_id = False) and
        ir_http._serve_page() picks with order='website_id asc'. In
        PostgreSQL NULL sorts first, so a site-specific '/' page would
        never be served. Write to the global page instead of creating a
        second one.
        """
        page = self.env['website.page'].search([
            ('url', '=', '/'),
            ('website_id', 'in', [site.id, False]),
        ], limit=1, order='website_id asc')
        if page and page.view_id:
            page.view_id.arch = (
                '<t t-name="%s"><t t-call="website.layout">%s</t></t>'
                % (page.view_id.key, HOMEPAGE)
            )
            page.view_id.invalidate_model(['arch'])

    def _seed_footer(self, site):
        footer = self.env['ir.ui.view'].search([
            ('key', '=', 'website.footer_custom'),
            ('website_id', 'in', [site.id, False]),
        ], limit=1, order='website_id desc')
        if footer:
            footer.arch = (
                '<data inherit_id="website.layout" name="Elevata Footer">'
                '<xpath expr="//div[@id=\'footer\']" position="replace">'
                '<div id="footer" class="o_footer oe_structure '
                'oe_structure_solo" t-ignore="true" t-if="not no_footer">'
                + FOOTER +
                '</div></xpath></data>'
            )
            footer.invalidate_model(['arch'])

    def _seed_menus(self, site):
        Menu = self.env['website.menu']
        root = site.menu_id
        if not root:
            return

        # Update existing defaults
        home = Menu.search([('parent_id', '=', root.id),
                            ('url', 'in', ['/', '/home'])], limit=1)
        if home:
            home.name = 'Hem'
            home.sequence = 10
        contact = Menu.search([('parent_id', '=', root.id),
                               ('url', '=', '/contactus')], limit=1)
        if contact:
            contact.name = 'Kontakta oss'
            contact.sequence = 90

        def menu(name, url, seq, parent=None):
            rec = Menu.search([
                ('parent_id', '=', (parent or root).id),
                ('url', '=', url),
            ], limit=1)
            vals = {
                'name': name,
                'url': url,
                'sequence': seq,
                'parent_id': (parent or root).id,
                'website_id': site.id,
            }
            if rec:
                rec.write(vals)
            else:
                Menu.create(vals)
            return rec

        for url, title, _body, seq in self.PAGES:
            menu(title, '/' + url, seq)
        menu('Jobba@elevata', '/jobs', 45)

        # Integritetspolicy ligger under Övrigt — ingen toppmeny direkt.
        top_policy = Menu.search([
            ('parent_id', '=', root.id), ('url', '=', '/integritetspolicy')])
        top_policy.unlink()

        ovrigt = menu('Övrigt', '#', 80)
        menu('Integritetspolicy', '/integritetspolicy', 10, parent=ovrigt)
