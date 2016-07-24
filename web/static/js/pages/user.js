define(['jquery', 'handlebars', 'main', 'text!templates/user.html', 'text!templates/error.html'], function(
    $, Handlebars, main, tpl, tplError) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.ajaxGet('/users').then(function(data) {
                if (data.status == 'success') {
                    data.data['API_URL'] = main.getApiUrl();
                    $('#section-content').html(template(data.data));
                    bind();
                } else {
                    $('#section-content').html(templateError({
                        'message': data.message
                    }));
                }
            });

            function showAlert(msg) {
                $('#helpBlock').focus();
                $('#helpBlock').html(
                    '<div class="alert alert-warning alert-dismissible fade in" role="alert">' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                    '<strong>' + msg + '</strong>' +
                    '</div>'
                );
            }

            function getCookie(name) {
                var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
                return r ? r[1] : undefined;
            }

            function bind(){

              $('#removeForm').submit(function() {
                  event.preventDefault();

                  var formData = {
                      '_xsrf': getCookie("_xsrf"),
                      'email': $('#removeEmail').val(),
                  };

                  $.ajax({
                      type: 'POST',
                      url: $('#api_url').val() + '/authentication/archive',
                      xhrFields: {
                          withCredentials: true
                      },
                      complete: function(msg) {
                          window.location.href = '/';
                      },
                      crossDomain: true,
                      error: function(jqXHR, exception) {
                          var msg = {
                              'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception
                          };
                          showAlert(msg);
                      }
                  });
              });
            }
        }
    }
});
