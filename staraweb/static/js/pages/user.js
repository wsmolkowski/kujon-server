define(['jquery', 'handlebars', 'main', 'text!templates/user.html', 'text!templates/error.html'], function($, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callUsers(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data.data));
                } else {
                    $('#page').html(templateError(data));
                }
            });

            //a tutaj możesz np. zapiąć listenery
        }
    }    
});