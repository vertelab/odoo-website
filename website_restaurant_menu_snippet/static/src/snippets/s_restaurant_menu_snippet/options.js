odoo.define('website_restaurant_menu_snippet.s_restaurant_menu_snippet_options', function (require) {
    'use strict';

    const options = require('web_editor.snippets.options');
    const core = require('web.core');
    const s_dynamic_snippet_carousel_options = require('website.s_dynamic_snippet_carousel_options');
    var wUtils = require('website.utils');


    const dynamicRestaurantMenuSnippetOptions = options.Class.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.modelNameFilter = 'product.product';
            this.productCategories = {};
        },

        async onBuilt() {
            this._super.apply(this, arguments);

            this.$target[0].dataset['snippet'] = 's_dynamic_snippet_restaurant_menu';
            await this._setOptionsDefaultValues();

            const classList = [...this.$target[0].classList];
            if (classList.includes('d-none') && !classList.some(className => className.match(/^d-(md|lg)-(?!none)/))) {
                // Remove the 'd-none' of the old template if it is not related to
                // the visible on mobile option.
                this.$target[0].classList.remove('d-none');
            }
            return this._refreshPublicWidgets();
        },

        async _setOptionsDefaultValues() {
            this.options.wysiwyg.odooEditor.observerUnactive();
            const filterProductCategories = this.$el.find("we-select[data-attribute-name='productCategoryId'] we-selection-items we-button");
            if (filterProductCategories.length > 0) {
                this._setOptionValue('productCategoryId', 'all');
                this._setOptionValue('numberOfRecords', 16);
            }
            this.options.wysiwyg.odooEditor.observerActive();
        },

        _fetchProductCategories: function () {
            return this._rpc({
                model: 'pos.category',
                method: 'search_read',
                kwargs: {
                    domain: wUtils.websiteDomain(this),
                    fields: ['id', 'name'],
                }
            });
        },

        _renderCustomXML: async function (uiFragment) {
            await this._super.apply(this, arguments);
            await this._renderProductCategorySelector(uiFragment);
        },

        _renderProductCategorySelector: async function (uiFragment) {
            const productCategories = await this._fetchProductCategories();
            for (let index in productCategories) {
                this.productCategories[productCategories[index].id] = productCategories[index];
            }
            const productCategoriesSelectorEl = uiFragment.querySelector('[data-name="product_category_opt"]');
            return this._renderSelectUserValueWidgetButtons(productCategoriesSelectorEl, this.productCategories);
        },

        _renderSelectUserValueWidgetButtons: async function (selectUserValueWidgetElement, data) {
            for (let id in data) {
                const button = document.createElement('we-button');
                button.dataset.selectDataAttribute = id;
                if (data[id].thumb) {
                    button.dataset.img = data[id].thumb;
                } else {
                    button.innerText = data[id].name;
                }
                selectUserValueWidgetElement.appendChild(button);
            }
        },

        _setOptionValue: function (optionName, value) {
            if (this.$target.get(0).dataset[optionName] === undefined || this.isOptionDefault[optionName]) {
                this.$target.get(0).dataset[optionName] = value;
            }
        },

    })
    options.registry.dynamic_restaurant_menu_snippet = dynamicRestaurantMenuSnippetOptions;

    return dynamicRestaurantMenuSnippetOptions;
});

