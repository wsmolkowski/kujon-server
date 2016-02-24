define(['jquery', 'handlebars', 'main', 'text!templates/register.html','text!templates/error.html'], function($, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
        
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callUsoses(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError({'message': data.data}));
                }
            });

            //a tutaj możesz np. zapiąć listenery
        }
    }    
});