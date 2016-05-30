define(['jquery', 'handlebars', 'main', 'text!templates/user.html', 'text!templates/error.html'], function(
$, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callUsers(function(data){
                if (data.status == 'success'){
                    data.data['API_URL'] = main.getApiUrl();
                    $('#page-content').html(template(data.data));
                } else {
                    $('#page-content').html(templateError({'message': data.message}));
                }
            });

            //a tutaj możesz np. zapiąć listenery
        }
    }    
});