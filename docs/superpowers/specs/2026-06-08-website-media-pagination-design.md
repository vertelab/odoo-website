# Spec: Media Library Pagination för Odoo Website

**Modul:** `website_media_pagination`  
**Datum:** 2026-06-08  
**Odoo-version:** 18.0  

## 1. Problem

Media library-dialogen i Odoo Website editorn ("Insert Media") använder idag en "Load more"-knapp som laddar 30 bilder i taget. För användare med många bilder (100+) blir det oöverskådligt — man ser inte var i biblioteket man befinner sig, hur många bilder som finns, eller hur man snabbt navigerar till en specifik sida.

## 2. Mål

Ersätta "Load more" med full paginering i media library-dialogen:
- Sidnumrering (1, 2, 3...) med hopp till första/sista sidan
- Väljbar sidstorlek (12, 24, 30, 60, 120 bilder per sida)
- Fungerar i båda editorimplementationerna (`html_editor` och `web_editor`)

## 3. Lösning

### 3.1 Arkitektur

Patch-baserad approach — en ny Odoo-modul som utökar befintliga komponenter med Odoos `patch()`-funktion, identiskt med hur `website`-modulen redan patchar `ImageSelector`.

```
website_media_pagination/
├── __init__.py                    # tom
├── __manifest__.py                # beroende: website
└── static/
    ├── src/js/
    │   └── media_pagination.js    # JS-patch för FileSelector i båda editorerna
    ├── src/xml/
    │   └── media_pagination.xml   # QWeb-sektion för pagineringskontroller
    └── src/scss/
        └── media_pagination.scss  # styling för paginerings-UI
```

### 3.2 Vad som patchas

| Mål | Editor | Modul-sökväg |
|-----|--------|--------------|
| `FileSelector` klass | `html_editor` | `@html_editor/main/media/media_dialog/file_selector` |
| `FileSelector` klass | `web_editor` | `@web_editor/components/media_dialog/file_selector` |

Templates patchas via QWeb `t-extend` + `t-jquery` i `media_pagination.xml` — ersätter "Load more"-blocket i båda template-varianterna (`html_editor.FileSelector` och `web_editor.FileSelector`). Detta är standard Odoo-mekanism för QWeb-template-arv och fungerar även för OWL-komponenters templates.

### 3.3 Ändringar — JS (media_pagination.js)

**Nytt state** som läggs till:

```js
currentPage: 1
totalCount: 0
pageSize: 30             // default, från NUMBER_OF_ATTACHMENTS_TO_DISPLAY
```

**Patched `fetchAttachments(limit, offset)`:**  
Efter `search_read`, gör även `orm.call('ir.attachment', 'search_count', [this.attachmentsDomain])` och spara i `state.totalCount`.

**Ny metod `get totalPages()`:**  
`Math.ceil(this.state.totalCount / this.state.pageSize)` — använder dynamisk sidstorlek.

**Ny metod `goToPage(page)`:**
- Validerar att sidan är inom 1..totalPages
- Anropar `fetchAttachments(pageSize, (page-1) * pageSize)` via `KeepLast`
- Ersätter `state.attachments` helt (append:ar inte)
- Uppdaterar `state.currentPage`

**Ny metod `handlePageSizeChange(newSize)`:**
- Sätter `state.pageSize = newSize`
- Nollställer `currentPage = 1`
- Återhämtar bilder med ny limit/offset

**Patched `search()`:**  
Nollställer `currentPage = 1` efter att sökningen är klar.

**Patched `handleLoadMore()`:**  
Triggar `goToPage(currentPage + 1)` istället för append av batch.

### 3.4 Template-ändringar — media_pagination.xml

Ersätter "Load more"-blocket (raderna 60-72 i `html_editor.FileSelector` / `web_editor.FileSelector`) med:

```xml
<div class="o_we_pagination d-flex flex-wrap justify-content-between align-items-center gap-2 px-3">
    <div class="d-flex align-items-center gap-3">
        <span class="o_we_pagination_info text-muted small">
            Showing 1–30 of 120
        </span>
        <div class="o_we_pagination_page_size d-flex align-items-center">
            <label class="text-muted small">Per page:</label>
            <select class="form-select form-select-sm">
                <option value="12">12</option>
                <option value="24">24</option>
                <option value="30" selected>30</option>
                <option value="60">60</option>
                <option value="120">120</option>
            </select>
        </div>
    </div>
    <nav class="o_we_pagination_nav">
        <ul class="pagination pagination-sm mb-0">
            <li><button class="page-link" title="First">«</button></li>
            <li><button class="page-link">‹</button></li>
            <li class="active"><button class="page-link">1</button></li>
            <li><button class="page-link">2</button></li>
            <li><button class="page-link">3</button></li>
            <li class="disabled"><span class="page-link">…</span></li>
            <li><button class="page-link">12</button></li>
            <li><button class="page-link">›</button></li>
            <li><button class="page-link" title="Last">»</button></li>
        </ul>
    </nav>
</div>
```

Där `paginationPages` är en computed-getter som genererar sidnummer med ellips-förkortning — max 7 sidnummer visas, med `…` för hopp över större intervall (samma mönster som Odoos `portal_pager`). Första och sista sidan visas alltid.

Scroll-knappen (`o_scroll_attachments`) tas bort i samma patch — den är inte nödvändig när användaren kan navigera direkt via sidnummer.

### 3.5 Styling — media_pagination.scss

Bootstrap `.pagination` används med modifierare:
- `.o_we_pagination` — marginaler/anpassning i media dialog
- `.o_we_pagination_info` — "Showing X–Y of Z"
- `.o_we_pagination_nav` — högerställd navigation
- `.o_hide_loading`-hantering för att dölja paginering under fetch (samma mönster som befintlig "load more"-flicker-fix)

### 3.6 Beteende för library media (Illustrations)

Paginering påverkar **enbart** `ir.attachment`-delen (databasbilder). Library media (Illustrations från Odoos API) fortsätter använda "load more" internt, eftersom API-et inte returnerar totalt antal på ett sätt som stödjer sidnumrering. Detta är acceptabelt eftersom illustrations-sökningar vanligtvis har färre träffar.

## 4. Gränssnitt — före/efter

**Före:**  
```
[Sökfält] [Upload]  
[ bild ] [ bild ] [ bild ] [ bild ]
[ bild ] [ bild ] [ bild ] [ bild ]
            [Load more...]
```

**Efter:**  
```
[Sökfält] [Upload]  
[ bild ] [ bild ] [ bild ] [ bild ]
[ bild ] [ bild ] [ bild ] [ bild ]
Showing 1–30 of 87 [Per page: 30 ▼]    « ‹ 1 2 3 4 5 … 12 › »
```

## 5. Beroenden

- `website` (som drar in `web_editor` och `html_editor`)

## 6. Testning

- Öppna media dialogen via "Insert Media" i website editor
- Verifiera att pagineringskontroller visas
- Navigera mellan sidor (prev/next, första/sista, klicka på sidnummer)
- Ändra sidstorlek (12, 24, 30, 60, 120) — verifiera att antal bilder per sida ändras och att sidnumrering räknas om
- Sök — verifiera att paginering återställs till sida 1
- Ladda upp ny bild — verifiera att den visas på sida 1
- Radera bild — verifiera att paginering uppdateras
- Testa med html_editor (ny editor) och web_editor (legacy)
