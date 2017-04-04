$(document).ready(function(){
    $("input[name=search]").keyup(function(){
        openerp.jsonRpc("/search_response", "call", {
            'search': $(this).val(),
        }).done(function(data){
            console.log(data);
            content_front = '<div class="result_suggestion">';
            content_behind = '</div>';
            content = '';
            $.each(data, function(key, info) {
                if (data[key]['model_record'] == 'product.template'){
                    c = '<li style="list-style-type: none;"><a style="color: #333; padding: 3px 20px; clear: both; font-weight: normal;" href="/shop/product/' + data[key]['res_id'] + '">' + data[key]['name'] + '</a></li>';
                    content += c;
                }
            });
            $(".result_suggestion").html(content_front + content + content_behind)
        });
    });
});
