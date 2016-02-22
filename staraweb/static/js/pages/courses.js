define(['jquery', 'handlebars', 'main', 'text!templates/courses.html', 'text!templates/error.html'], function($, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callCourseseditions(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError(data));
                }
            });
            
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});