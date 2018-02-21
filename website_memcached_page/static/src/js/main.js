// add ?cache_invalidate to url
function start_edit() {
    //~ var url = window.location.protocol + "//" + window.location.host + window.location.pathname;
    var url = window.location.pathname;
    openerp.jsonRpc("/remove_cached_page", "call", {
        'url': url
    }).done(function(data){
        //~ if (history.pushState) {
            //~ var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?cache_invalidate';
            //~ window.history.pushState({path:newurl}, '', newurl);
        //~ }
    });
}
