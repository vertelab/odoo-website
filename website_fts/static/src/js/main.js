$(document).ready(function(){
    $("input[name=search]").keyup(function(){
        openerp.jsonRpc("/search_term", "call", {
            'search': $(this).val(),
        }).done(function(data){
            console.log(data);
        });
    });
});
