/** @odoo-module **/
import options from '@web_editor/js/editor/snippets.options';
//import core from 'web.core';
import { rpc } from "@web/core/network/rpc";
import s_dynamic_snippet_carousel_options from "@website/snippets/s_dynamic_snippet_carousel/options";
import wUtils from "@website/js/utils";



const dynamicRestaurantMenuSnippetOptions = options.Class.extend({

     init: function () {
        console.log("options.js: init")
        this._super.apply(this, arguments);
        this.modelNameFilter = 'product.product';
        this.productCategories = {};
        
        this.isOptionDefault = {};
    },

    async onBuilt() {
        console.log("options.js: onBuilt")
        await this._super.apply(this, arguments);

//        this.$target[0].dataset['snippet'] = 's_dynamic_snippet_restaurant_menu';

        if (this._isNewSnippet()) {
            await this._setOptionsDefaultValues();
        }
//        const classList = [...this.$target[0].classList];
//        if (classList.includes('d-none') && !classList.some(className => className.match(/^d-(md|lg)-(?!none)/))) {
//            // Remove the 'd-none' of the old template if it is not related to
//            // the visible on mobile option.
//            this.$target[0].classList.remove('d-none');
//        }
        return this._refreshPublicWidgets();
    },
    
    /** 
     * @private
     * @returns {boolean}
     */
     
     _isNewSnippet: function() {
        const dataset = this.$target[0].dataset;
        return !dataset.productCategoryId && !dataset.templateKey;
    },    

    async _setOptionsDefaultValues() {
        console.log("options.js: _setOptionsDefaultValues")
        this.options.wysiwyg.odooEditor.observerUnactive();
        
        if (!this.$target[0].dataset.productCategoryId) {
            const filterProductCategories = this.$el.find("we-select[data-attribute-name='productCategoryId'] we-selection-items we-button");
            if (filterProductCategories.length > 0) {
                this._setOptionValue('productCategoryId', 'all');
            }
        }
        if (!this.$target[0].dataset.templateKey) {
            this._setOptionValie('templateKey', 'dynamic_filter_template_pos_category_restaurant_menu_1');
        }
        this.options.wysiwyg.odooEditor.observerActive();
    },


    _fetchProductCategories: function () {
        console.log("options.js: _fetchProductCategories")
        return this.orm.searchRead("pos.category", wUtils.websiteDomain(this), ["id", "name"]);
    },
    /**
     *
     * @override
     * @private
     */
    _renderCustomXML: async function (uiFragment) {
        console.log("options.js: _renderCustomXML")
        await this._super.apply(this, arguments);
        await this._renderProductCategorySelector(uiFragment);
    },
    /**
     * Renders the product categories option selector content into the provided uiFragment.
     * @private
     * @param {HTMLElement} uiFragment
     */
    _renderProductCategorySelector: async function (uiFragment) {
        console.log("options.js: _renderProductCategorySelector")
        const publishedCategories = await this._fetchProductCategories();

        for (let index in publishedCategories) {
            this.productCategories[publishedCategories[index].id] = publishedCategories[index];
        }
        const productCategoriesSelectorEl = uiFragment.querySelector('[data-name="product_category_opt"]');
        return this._renderSelectUserValueWidgetButtons(productCategoriesSelectorEl, this.productCategories);
    },

    _renderSelectUserValueWidgetButtons: async function (selectUserValueWidgetElement, data) {
        console.log("options.js: _renderSelectUserValueWidgetButtons")
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
        console.log("options.js: _setOptionValue körs")
        this.$target.get(0).dataset[optionName] = value;
    },
    
    async onTemplateKey(templateKey) {
        console.log("onTemplateKey körs med:", templateKey);
        this.$target.get(0).dataset.templateKey = templateKey;
        await this._refreshPublicWidgets();
    }

})

options.registry.dynamic_restaurant_menu_snippet = dynamicRestaurantMenuSnippetOptions;

return dynamicRestaurantMenuSnippetOptions;
