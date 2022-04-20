odoo.define('website_portal_actions.portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const {_t, qweb} = require('web.core');
    const ajax = require('web.ajax');

    publicWidget.registry.PortalHomeActionCounters = publicWidget.Widget.extend({
        selector: '.o_portal_my_home',

        start: function () {
            var def = this._super.apply(this, arguments);
            this._updateActivitiesCounters();
            return def;
        },

        async _updateActivitiesCounters(elem) {
            const numberRpc = 3;
            const needed = this.$('[data-placeholder_activities_count]')
                                    .map((i, o) => $(o).data('placeholder_activities_count'))
                                    .toArray();
            const counterByRpc = Math.ceil(needed.length / numberRpc);  // max counter, last can be less

            const proms = [...Array(Math.min(numberRpc, needed.length)).keys()].map(async i => {
                await this._rpc({
                    route: "/activities/counters",
                    params: {
                        counters: needed.slice(i * counterByRpc, (i + 1) * counterByRpc)
                    },
                }).then(data => {
                    Object.keys(data).map(k => this.$("[data-placeholder_activities_count='" + k + "']").text(data[k]));
                });
            });
            return Promise.all(proms);
        },
    })
})
