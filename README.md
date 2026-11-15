# odoo-website — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **14** |
| Grenar i repot | `10.0`, `12.0`, `12.0-AFC-261`, `13.0`, `14.0`, `16.0`, `17.0`, `18.0`, `20.0`, `8.0`, `Dev-12.0`, `Dev-12.0-Fenix-Sprint-02`, `dart-app`, `dev`, `event_website_detailed_page`, `master`, `master10`, `memcached_porting`, `website-slides-section-fix`, `website-theme-demo-page-14-migration`, `website_dms_mediabank`, `website_document_activities_dev`, `website_myportal_listing_dev` |

## Moduler

- `crm_campaign_blog`
- `odoo_screen_capture`
- `toggle_record_on_portal`
- `website_ai`
- `website_ai_blog`
- `website_ai_event`
- `website_ai_hr`
- `website_crm_campaign`
- `website_event_portal_listing`
- `website_gallery_fix`
- `website_media_pagination`
- `website_memcached`
- `website_page_menu_form_view`
- `website_restaurant_menu_snippet`

## Blockerare

✅ Inga externa beroenden saknas i Odoo 19-kärnan eller OCA 19.0.

Modulerna kan troligen portas utan att vänta på externa bidrag.

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
