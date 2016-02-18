define(['jquery', 'handlebars', 'main', 'text!templates/courses.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
        
            var template = Handlebars.compile(tpl);
            
            var request_url = main.getApiUrl('/api/courseseditions/');

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
                },
                crossDomain: true,
                success:  function (data) {
                    if (data.status == 'success'){
                        $('#page').html(template(data));
                    } else {
                        $('#page').html(data.message);
                    }
                },
                error: function (err) {
                    console.log(err);
                }
            });
            
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});