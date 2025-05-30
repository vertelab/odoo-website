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
        this.modelNameFilter = 'pos.category';
        this.posCategories = {};
        
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
        return !dataset.posCategoryId && !dataset.templateKey;
    },    

    async _setOptionsDefaultValues() {
        console.log("options.js: _setOptionsDefaultValues")
        this.options.wysiwyg.odooEditor.observerUnactive();
        
        if (!this.$target[0].dataset.posCategoryId) {
            this._setOptionValue('posCategoryId', 'all');
        }
        if (!this.$target[0].dataset.templateKey) {
            this._setOptionValue('templateKey', 'dynamic_filter_template_pos_category_restaurant_menu_1');
        }
        if (!this.$target[0].dataset.numberOfRecords) {
            this._setOptionValue('numberOfRecords', '16');
        }
        
        this.options.wysiwyg.odooEditor.observerActive();
    },


    _fetchPosCategories: function () {
        console.log("options.js: _fetchPosCategories")
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
        await this._renderPosCategorySelector(uiFragment);
    },
    /**
     * Renders the product categories option selector content into the provided uiFragment.
     * @private
     * @param {HTMLElement} uiFragment
     */
    _renderPosCategorySelector: async function (uiFragment) {
        console.log("options.js: _renderPosCategorySelector")
        const publishedPosCategories = await this._fetchPosCategories();

        for (let index in publishedPosCategories) {
            this.posCategories[publishedPosCategories[index].id] = publishedPosCategories[index];
        }
        const posCategoriesSelectorEl = uiFragment.querySelector('[data-name="pos_category_opt"]');
        return this._renderSelectUserValueWidgetButtons(posCategoriesSelectorEl, this.posCategories);
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
    
    async onPosCategoryId(posCategoryId) {
        console.log("onPosCategoryId runs with:", posCategoryId);
        this.$target.get(0).dataset.posCategoryId = posCategoryId;
        await this._refreshPublicWidgets();
    },
    
    async onTemplateKey(templateKey) {
        console.log("onTemplateKey körs med:", templateKey);
        this.$target.get(0).dataset.templateKey = templateKey;
        await this._refreshPublicWidgets();
    },
    
    async onNumberOfRecords(numberOfRecords) {
        console.log("onNumberOfRecords runs with:", numberOfRecords);
        this.$target.get(0).dataset.numberOfRecords = numberOfRecords;
        await this._refreshPublicWidgets();
    }

})

options.registry.dynamic_restaurant_menu_snippet = dynamicRestaurantMenuSnippetOptions;

return dynamicRestaurantMenuSnippetOptions;
