define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html', 'text!templates/error.html'], function($, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            var request_url = main.getApiUrl('/api/lecturers/');

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
                        $('#page').html(templateError(data));
                    }
                },
                error: function(jqXHR, exception) {
                    var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.responseText + ' exception: ' + exception};
                    $('#page').html(templateError(msg));
                }
            });
        }
    }    
});