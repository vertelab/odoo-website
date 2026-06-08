import { patch } from "@web/core/utils/patch";
import { FileSelector as HtmlFileSelector } from "@html_editor/main/media/media_dialog/file_selector";
import { FileSelector as WebFileSelector } from "@web_editor/components/media_dialog/file_selector";
import { useEffect } from "@odoo/owl";

function buildPaginationHTML(component) {
    const currentPage = component.state.currentPage;
    const totalPages = component.totalPages;
    const totalCount = component.state.totalCount;
    const pageSize = component.state.pageSize;
    const paginationPages = component.paginationPages;

    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalCount);

    let pagesHTML = "";
    for (const p of paginationPages) {
        if (p === "...") {
            pagesHTML += '<li class="page-item disabled"><span class="page-link">\u2026</span></li>';
        } else {
            pagesHTML += `<li class="page-item${p === currentPage ? " active" : ""}"><button class="page-link" data-page="${p}">${p}</button></li>`;
        }
    }

    let sizeOptions = [12, 24, 30, 60, 120]
        .map((s) => `<option value="${s}"${s === pageSize ? " selected" : ""}>${s}</option>`)
        .join("");

    return (
        '<div class="o_we_pagination d-flex flex-wrap justify-content-between align-items-center gap-2 px-3 pb-3">' +
        '<div class="d-flex align-items-center gap-3">' +
        '<span class="o_we_pagination_info text-muted small">' +
        `Showing ${start}\u2013${end} of ${totalCount}</span>` +
        '<div class="o_we_pagination_page_size d-flex align-items-center">' +
        '<label class="text-muted small">Per page:</label>' +
        `<select class="form-select form-select-sm" data-page-size="1">${sizeOptions}</select>` +
        "</div></div>" +
        '<nav class="o_we_pagination_nav">' +
        '<ul class="pagination pagination-sm mb-0">' +
        `<li class="page-item${currentPage <= 1 ? " disabled" : ""}"><button class="page-link" data-page="1" ${currentPage <= 1 ? "disabled" : ""} title="First page">\u00ab</button></li>` +
        `<li class="page-item${currentPage <= 1 ? " disabled" : ""}"><button class="page-link" data-page="${currentPage - 1}" ${currentPage <= 1 ? "disabled" : ""}>\u2039</button></li>` +
        pagesHTML +
        `<li class="page-item${currentPage >= totalPages ? " disabled" : ""}"><button class="page-link" data-page="${currentPage + 1}" ${currentPage >= totalPages ? "disabled" : ""}>\u203a</button></li>` +
        `<li class="page-item${currentPage >= totalPages ? " disabled" : ""}"><button class="page-link" data-page="${totalPages}" ${currentPage >= totalPages ? "disabled" : ""} title="Last page">\u00bb</button></li>` +
        "</ul></nav></div>"
    );
}

function patchFileSelector(FileSelector) {
    patch(FileSelector.prototype, {
        setup() {
            super.setup(...arguments);
            this.state.currentPage = 1;
            this.state.totalCount = 0;
            this.state.pageSize = this.NUMBER_OF_ATTACHMENTS_TO_DISPLAY;

            useEffect(
                () => {
                    const loadMoreEl = this.loadMoreButtonRef?.el;
                    if (!loadMoreEl || !loadMoreEl.parentNode) return;

                    const parent = loadMoreEl.parentNode;
                    let container = parent.querySelector(".o_mp_pagination_container");

                    if (this.totalPages > 1) {
                        loadMoreEl.style.display = "none";
                        if (!container) {
                            container = document.createElement("div");
                            container.className = "o_mp_pagination_container";
                            loadMoreEl.insertAdjacentElement("afterend", container);
                        }
                        container.innerHTML = buildPaginationHTML(this);
                        container.querySelectorAll("[data-page]").forEach((btn) => {
                            btn.addEventListener("click", (ev) =>
                                this.goToPage(parseInt(ev.currentTarget.dataset.page))
                            );
                        });
                        const sizeSelect = container.querySelector("[data-page-size]");
                        if (sizeSelect) {
                            sizeSelect.addEventListener("change", (ev) =>
                                this.handlePageSizeChange(parseInt(ev.target.value))
                            );
                        }
                    } else {
                        loadMoreEl.style.display = "";
                        if (container) {
                            container.remove();
                        }
                    }
                },
                () => [
                    this.state.attachments.length,
                    this.state.currentPage,
                    this.state.totalCount,
                    this.state.pageSize,
                    this.state.needle,
                ]
            );
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
            const totalCount = await this.orm.call("ir.attachment", "search_count", [
                this.attachmentsDomain,
            ]);
            this.state.totalCount = totalCount;
            return result;
        },

        async goToPage(page) {
            if (page < 1 || page > this.totalPages) return;
            this.state.currentPage = page;
            const pageSize = this.state.pageSize;
            return this.keepLast
                .add(this.fetchAttachments(pageSize, (page - 1) * pageSize))
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
