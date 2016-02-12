define(['jquery', 'handlebars', 'main', 'text!templates/user.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            var config = main.getConfig();
            console.log(config);

            var request_url = config['USOS_API'] + '/api/users/';
            console.log(request_url);

            $.ajax({
                beforeSend: function ( xhr ) {
                    //xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.setRequestHeader('Access-Control-Request-Method', 'GET');
                    xhr.setRequestHeader('Access-Control-Request-Headers', '*');
                    xhr.withCredentials = true;
                },
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