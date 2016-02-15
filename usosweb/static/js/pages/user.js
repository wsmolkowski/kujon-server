define(['jquery', 'handlebars', 'main', 'text!templates/user.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            var request_url = main.getApiUrl('/api/users/');

            $.ajax({
                type: 'GET',
                url: request_url,
                success:  function (data) {
                    $('#page').html(template(data.data[0]));
                },
                error: function (err) {
                    console.log(err);
                }
            });
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});