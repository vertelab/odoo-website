function loadConsumerRegisterMessageBox() {
    $("#open_msgbox").click(function(){
        $(this).closest('#message_box').find("#msgbox").removeClass('hidden');
        $(this).addClass('hidden');
        $(this).closest('#message_box').find("#close_msgbox").removeClass('hidden');
        $(this).closest('#message_box').find("#send_msgbox").removeClass('hidden');
    });

    $("#close_msgbox").click(function(){
        $(this).closest('#message_box').find("#msgbox").addClass('hidden');
        $(this).closest('#message_box').find("#send_msgbox").addClass('hidden');
        $(this).addClass('hidden');
        $(this).closest('#message_box').find("#open_msgbox").removeClass('hidden');
    });

    $("#send_msgbox").click(function(){
        var self = $(this);
        openerp.jsonRpc("/website_consumer_register_message_send", "call", {
            "issue_id": self.data('value'),
            "msg_body": self.closest("#message_box").find("#msgbox").val()
        }).done(function(data){
            $("#message_box").load(
                location.href + " #message_box",
                function(response, status, xhr) {
                    loadConsumerRegisterMessageBox();
                });
        });
    });
};

$(document).ready(function(){

    $("form.form-navtabs-validation div.tab-pane input, form.form-navtabs-validation div.tab-pane select").on('invalid', function (e, data) {
        // Switch to tab of invalid input or select
        self = $(this);
        tab = self.parents('div.tab-pane');
        menu = $('ul.nav-tabs > li > a[href="#' + tab.attr('id') + '"]').parent('li');
        self.parents('div.tab-content').find('div.tab-pane').removeClass('active');
        tab.addClass('active');
        tab.addClass('in');
        menu.siblings('li').removeClass('active');
        menu.addClass('active');
    });

    loadConsumerRegisterMessageBox();

    $(".oe_consumer_register_copy_address").change(function() {
        // Copy values from one address type to another
        self = $(this);
        if(this.checked) {
            var names = address_type = self.attr('name').split('_');
            var address_type = names[0];
            var copy_type = names[names.length - 1];
            $('div#' + address_type).find('input').each(function (i, el){
                if (el.name.substring(0, address_type.length + 1) == address_type + '_') {
                    var name = copy_type + el.name.substring(address_type.length);
                    el.value = $('input[name="' + name + '"]').attr('value');
                }
            });
            $('div#' + address_type).find('select').each(function (i, el){
                if (el.name.substring(0, address_type.length + 1) == address_type + '_') {
                    var name = copy_type + el.name.substring(address_type.length);
                    var value = $('select[name="' + name + '"]').find('option:selected').val();
                    $(el).find('option[value="' + value + '"]').attr('selected', 'selected')
                }
            });
        }
    });

    $("i#remove_img_contact").click(function(){
        var self = $(this);
        openerp.jsonRpc("/consumer_register/contact/remove_img_contact", "call", {
            'partner_id': self.data("partner_id")
        }).done(function(data){
            if (data) {
                $("img#contact_img").attr("src", "");
                self.find("input#contact_img").val('1');
                self.addClass("hidden");
            }
        });
    });

    $("select[name='category_id']").select2();

});

function RRpwReset(user_id, partner_id) {
    openerp.jsonRpc("/consumer_register/contact/pw_reset", "call", {
        'user_id': user_id,
        'partner_id': partner_id,
    }).done(function(data){
        window.alert(data);
    });
}
