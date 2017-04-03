$(document).ready(function(){
    $("input[name='search']").keyup(function() {
        console.log($(this).val());
    });
    //~ $("input[name=search]").change(function(){
        //~ openerp.jsonRpc("/get_suggestion_terms", "call", {

        //~ }).done(function(data){
        //~ });
    //~ });
});
