define(['jquery', 'handlebars', 'text!templates/user.html'], function($, Handlebars, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            
            //tutaj możesz zrobić np. wywołanie JSON

            $.ajax({
                type: 'GET',
                url: 'http://localhost:8881/api/users/',
                success:  function (data) {
                    $('#page').html(template(data));
                },
                error: function (err) {
                    console.log(err);
                }
            });

            //a tutaj możesz np. zapiąć listenery
        }
    }    
});