$(document).ready(function(){
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
        openerp.jsonRpc("/website_reseller_register_message_send", "call", {
            "issue_id": self.data('value'),
            "msg_body": self.closest("#message_box").find("#msgbox").val()
        }).done(function(data){
            $("#message_box").load(location.href + " #message_box");
            $("#msgbox").addClass('hidden');
            $("#send_msgbox").addClass('hidden');
            $("#close_msgbox").addClass('hidden');
            $("#open_msgbox").removeClass('hidden');
        });
    });
});
