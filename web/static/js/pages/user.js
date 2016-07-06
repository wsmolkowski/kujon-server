define(['jquery', 'handlebars', 'main', 'text!templates/user.html', 'text!templates/error.html'], function(
$, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.ajaxGet('/users').then(function(data){
                if (data.status == 'success'){
                    data.data['API_URL'] = main.getApiUrl();
                    $('#section-content').html(template(data.data));
                } else {
                    $('#section-content').html(templateError({'message': data.message}));
                }
            });
        }
    }    
});