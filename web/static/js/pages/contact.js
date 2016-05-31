define(['jquery', 'handlebars', 'text!templates/contact.html'],
function($, Handlebars, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            $('#page-content').html(template());

            function getCookie(name) {
                var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
                return r ? r[1] : undefined;
            }

            $('#contactSubmit').click(function(){
                var formData = {
                    '_xsrf':    getCookie("_xsrf"),
                    'subject': $('#inputSubject').val(),
                    'message': $('#inputMessage').val(),
                };

                $.ajax({
                    type: "POST",
                    url: "/contact",
                    data: JSON.stringify(formData),
                    contentType: "application/json",
                    dataType: "json",
                    xhrFields: {
                        withCredentials: true
                    },
                    //crossDomain: true,
                    beforeSend: function(){
                        console.log(formData);
                    },
                    complete: function(){
                        //hideSpinner();
                    },
                    success:  function (data) {
                        console.log(data);
                    },
                    error: function(jqXHR, exception) {
                        var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception};
                        //$('#page').html(templateError(msg));
                        console.log(msg);
                    }
                });

                event.preventDefault();
            });
        }
    }
});