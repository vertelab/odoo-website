$(document).ready(function () {
    var bbbid = $('div.oe-bbb-join-meeting').data('bbbid');
    if (bbbid) {
        setInterval(function () {
            openerp.jsonRpc("/website_bbb/meeting/" + bbbid + "/is_running", "call", {}).done(function(data){
                if (data) {
                    $('.oe-bbb-meeting-closed').addClass('hidden');
                    $('.oe-bbb-meeting-running').removeClass('hidden');
                } else {
                    $('.oe-bbb-meeting-closed').removeClass('hidden');
                    $('.oe-bbb-meeting-running').addClass('hidden');
                }
            });
        }, 60000);
    }
});
