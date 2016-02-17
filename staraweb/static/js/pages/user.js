define(['jquery', 'handlebars', 'main', 'text!templates/user.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            var request_url = main.getApiUrl('/api/users/');

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
                },
                crossDomain: true,
                success:  function (data) {
                    if (data.status == 'success'){
                        $('#page').html(template(data.data[0]));
                    } else {
                        $('#page').html(data.message);
                    }
                },
                error: function (err) {
                    $('#page').html(err);
                }
            });
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});