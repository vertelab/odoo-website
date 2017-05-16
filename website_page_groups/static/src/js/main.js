$(document).ready(function() {
    $("#remove_groups").click(function(){
        var $data = $(this).parents(".js_publish_management:first");
        openerp.jsonRpc('/website_page_groups/set_groups', 'call', {'groups': $(this).data('groups'), 'page_id': $data.data('id')});
    });
    $("#set_groups").click(function(){
        var $data = $(this).parents(".js_publish_management:first");
        openerp.jsonRpc('/website_page_groups/set_groups', 'call', {'groups': $(this).data('groups'), 'page_id': $data.data('id')});
    });
});
