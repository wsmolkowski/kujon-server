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
                    $('#page').html(templateError({'message': data.message}));
                }
            });

            //a tutaj możesz np. zapiąć listenery
            $('.user-register-form').submit(function(){
                main.showSpinner();
                debugger;

                var formId = this.id;

                console.log(formId);

                main.hideSpinner();
            });
        }
    }    
});