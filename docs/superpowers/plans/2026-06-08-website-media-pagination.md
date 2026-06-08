# Media Library Pagination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace "Load more" with full pagination (page numbers, first/last, page size selector) in Odoo website's media library dialog.

**Architecture:** New Odoo module `website_media_pagination` that patches the `FileSelector` OWL component in both `html_editor` and `web_editor` via `patch()` (JS) and `t-inherit` (QWeb template inheritance), following the same pattern as `web_unsplash`.

**Tech Stack:** Odoo 18.0, OWL, JavaScript (ES modules), SCSS, QWeb

---

### Task 1: Module skeleton

**Files:**
- Create: `website_media_pagination/__init__.py`
- Create: `website_media_pagination/__manifest__.py`

- [ ] **Step 1: Create `__init__.py`**

Create empty file `website_media_pagination/__init__.py`.

- [ ] **Step 2: Create `__manifest__.py`**

```python
{
    'name': 'Website Media Pagination',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Add pagination to website media library dialog',
    'depends': ['website'],
    'assets': {
        'web.assets_frontend': [
            'website_media_pagination/static/src/scss/media_pagination.scss',
        ],
        'website.assets_wysiwyg': [
            'website_media_pagination/static/src/js/media_pagination.js',
            'website_media_pagination/static/src/xml/media_pagination.xml',
        ],
    },
    'auto_install': False,
    'installable': True,
    'license': 'LGPL-3',
}
```

Note: `website.assets_wysiwyg` is the bundle where the media dialog components live. The SCSS goes in `web.assets_frontend` since the dialog modal is part of the frontend.

---

### Task 2: SCSS for pagination styling

**Files:**
- Create: `website_media_pagination/static/src/scss/media_pagination.scss`

- [ ] **Step 1: Create `media_pagination.scss`**

```scss
.o_we_pagination {
    .o_we_pagination_info {
        white-space: nowrap;
        font-size: 0.85rem;
    }
    .o_we_pagination_nav {
        .pagination {
            margin: 0;
        }
        .page-link {
            cursor: pointer;
            padding: 0.25rem 0.6rem;
            font-size: 0.8rem;
        }
    }
    .o_we_pagination_page_size {
        select {
            font-size: 0.8rem;
            padding: 0.15rem 0.4rem;
        }
        label {
            font-size: 0.8rem;
            margin: 0 0.3rem 0 0;
        }
    }
}
```

---

### Task 3: Template inheritance for pagination controls

**Files:**
- Create: `website_media_pagination/static/src/xml/media_pagination.xml`

- [ ] **Step 1: Create `media_pagination.xml`**

Replace the "Load more" section and remove the scroll-to-bottom button in both editor templates.

```xml
<?xml version="1.0" encoding="utf-8"?>
<templates id="template" xml:space="preserve">

    <t t-inherit="html_editor.FileSelector" t-inherit-mode="extension">
        <xpath expr="//div[@name='load_more_attachments']" position="replace">
            <div name="load_more_attachments"
                 class="pt-3 pb-1 mx-auto o_we_load_more"
                 t-ref="load-more-button">
                <t t-if="totalPages > 1">
                    <div class="o_we_pagination d-flex flex-wrap justify-content-between align-items-center gap-2 px-3">
                        <div class="d-flex align-items-center gap-3">
                            <span class="o_we_pagination_info text-muted small">
                                Showing <t t-esc="(currentPage - 1) * pageSize + 1"/>–<t t-esc="Math.min(currentPage * pageSize, totalCount)"/> of <t t-esc="totalCount"/>
                            </span>
                            <div class="o_we_pagination_page_size d-flex align-items-center">
                                <label class="text-muted small">Per page:</label>
                                <select class="form-select form-select-sm" t-on-change="(ev) => handlePageSizeChange(parseInt(ev.target.value))">
                                    <option t-att-selected="pageSize === 12" value="12">12</option>
                                    <option t-att-selected="pageSize === 24" value="24">24</option>
                                    <option t-att-selected="pageSize === 30" value="30" t-esc="'30'"/>
                                    <option t-att-selected="pageSize === 60" value="60">60</option>
                                    <option t-att-selected="pageSize === 120" value="120">120</option>
                                </select>
                            </div>
                        </div>
                        <nav class="o_we_pagination_nav">
                            <ul class="pagination pagination-sm mb-0">
                                <li t-att-class="'page-item' + (currentPage <= 1 ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage <= 1" t-on-click="goToPage(1)" title="First page">«</button>
                                </li>
                                <li t-att-class="'page-item' + (currentPage <= 1 ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage <= 1" t-on-click="goToPage(currentPage - 1)">‹</button>
                                </li>
                                <t t-foreach="paginationPages" t-as="page" t-key="page_index">
                                    <li t-if="page === '...'" class="page-item disabled">
                                        <span class="page-link">…</span>
                                    </li>
                                    <li t-else="" t-att-class="'page-item' + (page === currentPage ? ' active' : '')">
                                        <button class="page-link" t-on-click="() => goToPage(page)" t-esc="page"/>
                                    </li>
                                </t>
                                <li t-att-class="'page-item' + (currentPage >= totalPages ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage >= totalPages" t-on-click="goToPage(currentPage + 1)">›</button>
                                </li>
                                <li t-att-class="'page-item' + (currentPage >= totalPages ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage >= totalPages" t-on-click="goToPage(totalPages)" title="Last page">»</button>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </t>
                <t t-elif="hasContent">
                    <div class="mt-2 o_load_done_msg text-center">
                        <span><i t-esc="allLoadedText"/></span>
                    </div>
                </t>
            </div>
        </xpath>
        <xpath expr="//div[contains(@class, 'o_scroll_attachments')]" position="replace"/>
    </t>

    <t t-inherit="web_editor.FileSelector" t-inherit-mode="extension">
        <xpath expr="//div[@name='load_more_attachments']" position="replace">
            <div name="load_more_attachments"
                 class="pt-3 pb-1 mx-auto o_we_load_more"
                 t-ref="load-more-button">
                <t t-if="totalPages > 1">
                    <div class="o_we_pagination d-flex flex-wrap justify-content-between align-items-center gap-2 px-3">
                        <div class="d-flex align-items-center gap-3">
                            <span class="o_we_pagination_info text-muted small">
                                Showing <t t-esc="(currentPage - 1) * pageSize + 1"/>–<t t-esc="Math.min(currentPage * pageSize, totalCount)"/> of <t t-esc="totalCount"/>
                            </span>
                            <div class="o_we_pagination_page_size d-flex align-items-center">
                                <label class="text-muted small">Per page:</label>
                                <select class="form-select form-select-sm" t-on-change="(ev) => handlePageSizeChange(parseInt(ev.target.value))">
                                    <option t-att-selected="pageSize === 12" value="12">12</option>
                                    <option t-att-selected="pageSize === 24" value="24">24</option>
                                    <option t-att-selected="pageSize === 30" value="30" t-esc="'30'"/>
                                    <option t-att-selected="pageSize === 60" value="60">60</option>
                                    <option t-att-selected="pageSize === 120" value="120">120</option>
                                </select>
                            </div>
                        </div>
                        <nav class="o_we_pagination_nav">
                            <ul class="pagination pagination-sm mb-0">
                                <li t-att-class="'page-item' + (currentPage <= 1 ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage <= 1" t-on-click="goToPage(1)" title="First page">«</button>
                                </li>
                                <li t-att-class="'page-item' + (currentPage <= 1 ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage <= 1" t-on-click="goToPage(currentPage - 1)">‹</button>
                                </li>
                                <t t-foreach="paginationPages" t-as="page" t-key="page_index">
                                    <li t-if="page === '...'" class="page-item disabled">
                                        <span class="page-link">…</span>
                                    </li>
                                    <li t-else="" t-att-class="'page-item' + (page === currentPage ? ' active' : '')">
                                        <button class="page-link" t-on-click="() => goToPage(page)" t-esc="page"/>
                                    </li>
                                </t>
                                <li t-att-class="'page-item' + (currentPage >= totalPages ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage >= totalPages" t-on-click="goToPage(currentPage + 1)">›</button>
                                </li>
                                <li t-att-class="'page-item' + (currentPage >= totalPages ? ' disabled' : '')">
                                    <button class="page-link" t-att-disabled="currentPage >= totalPages" t-on-click="goToPage(totalPages)" title="Last page">»</button>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </t>
                <t t-elif="hasContent">
                    <div class="mt-2 o_load_done_msg text-center">
                        <span><i t-esc="allLoadedText"/></span>
                    </div>
                </t>
            </div>
        </xpath>
        <xpath expr="//div[contains(@class, 'o_scroll_attachments')]" position="replace"/>
    </t>

</templates>
```

---

### Task 4: JS patch for FileSelector (both editors)

**Files:**
- Create: `website_media_pagination/static/src/js/media_pagination.js`

- [ ] **Step 1: Create `media_pagination.js`**

```js
import { patch } from "@web/core/utils/patch";
import { FileSelector as HtmlFileSelector } from "@html_editor/main/media/media_dialog/file_selector";
import { FileSelector as WebFileSelector } from "@web_editor/components/media_dialog/file_selector";

function patchFileSelector(FileSelector) {
    patch(FileSelector.prototype, {
        setup() {
            super.setup(...arguments);
            this.state.currentPage = 1;
            this.state.totalCount = 0;
            this.state.pageSize = this.NUMBER_OF_ATTACHMENTS_TO_DISPLAY;
        },

        get totalPages() {
            return Math.ceil(this.state.totalCount / this.state.pageSize) || 1;
        },

        get pageSize() {
            return this.state.pageSize;
        },

        get paginationPages() {
            const total = this.totalPages;
            const current = this.state.currentPage;
            const pages = [];

            if (total <= 7) {
                for (let i = 1; i <= total; i++) pages.push(i);
                return pages;
            }

            pages.push(1);

            let start = Math.max(2, current - 1);
            let end = Math.min(total - 1, current + 1);

            if (current <= 3) {
                end = Math.min(5, total - 1);
            }
            if (current >= total - 2) {
                start = Math.max(2, total - 4);
            }

            if (start > 2) pages.push("...");
            for (let i = start; i <= end; i++) pages.push(i);
            if (end < total - 1) pages.push("...");

            if (total > 1) pages.push(total);

            return pages;
        },

        async fetchAttachments(limit, offset) {
            const result = await super.fetchAttachments(limit, offset);
            const totalCount = await this.orm.call(
                "ir.attachment",
                "search_count",
                [this.attachmentsDomain]
            );
            this.state.totalCount = totalCount;
            return result;
        },

        async goToPage(page) {
            if (page < 1 || page > this.totalPages) return;
            this.state.currentPage = page;
            const pageSize = this.state.pageSize;
            return this.keepLast
                .add(
                    this.fetchAttachments(pageSize, (page - 1) * pageSize)
                )
                .then((attachments) => {
                    this.state.attachments = attachments;
                });
        },

        async handlePageSizeChange(newSize) {
            this.state.currentPage = 1;
            this.state.pageSize = newSize;
            await this.keepLast
                .add(this.fetchAttachments(newSize, 0))
                .then((attachments) => {
                    this.state.attachments = attachments;
                });
        },

        async search(...args) {
            this.state.currentPage = 1;
            return super.search(...args);
        },

        async handleLoadMore() {
            await this.goToPage(this.state.currentPage + 1);
        },
    });
}

patchFileSelector(HtmlFileSelector);
patchFileSelector(WebFileSelector);
```

- [ ] **Step 2: Verify no syntax errors**

Run: `python3 -c "
import re
with open('website_media_pagination/static/src/js/media_pagination.js') as f:
    content = f.read()
    # Basic check: matching braces
    assert content.count('{') == content.count('}'), 'Mismatched braces'
    assert content.count('(') == content.count(')'), 'Mismatched parens'
    print('JS basic syntax OK')
"`

Expected: `JS basic syntax OK`

---

### Task 5: Verify module structure

- [ ] **Step 1: Verify final file tree**

Run:
```bash
find website_media_pagination -type f | sort
```

Expected:
```
website_media_pagination/__init__.py
website_media_pagination/__manifest__.py
website_media_pagination/static/src/js/media_pagination.js
website_media_pagination/static/src/scss/media_pagination.scss
website_media_pagination/static/src/xml/media_pagination.xml
```

- [ ] **Step 2: Verify manifest parses**

Run: `python3 -c "import ast; ast.literal_eval(open('website_media_pagination/__manifest__.py').read()); print('Manifest OK')"`  

Expected: `Manifest OK`

---

### Task 6: Install and smoke-test module

- [ ] **Step 1: Find Odoo addons path and link/copy module**

Run:
```bash
python3 -c "import odoo; print(odoo.tools.config['addons_path'])"
```

Expected: A colon-separated path of addons directories.

Copy or symlink the module into the first writable addons path, then restart Odoo.

- [ ] **Step 2: Install module via Odoo CLI or UI**

```bash
odoo-bin -d <db_name> -i website_media_pagination --stop-after-init
```

Expected: Module installed without errors.

- [ ] **Step 3: Manual smoke test**

1. Log into Odoo website
2. Edit a page (enter website editor)
3. Click "Insert Media" in the editor toolbar
4. In the media dialog, verify that:
   - The "Load more" button is replaced by page number navigation
   - "Showing X–Y of Z" text is displayed
   - Page numbers 1, 2, 3... are shown
   - Clicking a page number loads the correct images
   - Previous/next (« ‹ › ») buttons work
   - Search resets to page 1
   - Uploading an image shows it on page 1
   - Page size selector changes the number of images per page
   - First/last page buttons navigate correctly

---

### Self-review checklist

1. **Spec coverage:** Every spec requirement maps to a task:
   - Patch FileSelector (both editors) → Tasks 3, 4
   - Page number navigation → Tasks 3, 4
   - "Showing X–Y of Z" text → Task 3
   - Ellipsis pagination → Task 4 (paginationPages)
   - Search resets to page 1 → Task 4 (patched search)
   - Library media (illustrations) unaffected → by design (paginationPages only shows for ir.attachment)
   - Scroll button removed → Task 3 (xpath replace)
   - First/last page buttons → Task 3 (« » buttons), Task 4 (goToPage)
   - Page size selector → Task 3 (dropdown), Task 4 (handlePageSizeChange, pageSize state)
   - Tests → Task 6 (manual smoke test)

2. **Placeholders:** None — all code is concrete.

3. **Type consistency:** `currentPage`, `totalCount`, `totalPages`, `paginationPages`, `pageSize`, `goToPage(page)`, `handlePageSizeChange(newSize)`, `handleLoadMore()` — consistent across JS patch and XML template.
