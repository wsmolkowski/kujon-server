define(['jquery', 'handlebars', 'text!templates/contact.html', 'text!templates/spinner.html',
'text!templates/modal_success.html', 'text!templates/modal_error.html'],
    function($, Handlebars, tpl, spinnerTpl, modalSuccess, modalError) {
        'use strict';
        return {
            render: function() {
                var template = Handlebars.compile(tpl);
                var templateSpinner = Handlebars.compile(spinnerTpl);
                var templateSuccess = Handlebars.compile(modalSuccess);
                var templateError = Handlebars.compile(modalError);

                $('#section-content').html(template());

                function getCookie(name) {
                    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
                    return r ? r[1] : undefined;
                }

                $('#contactSubmit').click(function() {
                    var formData = {
                        '_xsrf': getCookie("_xsrf"),
                        'subject': $('#inputSubject').val(),
                        'message': $('#inputMessage').val(),
                    };

                    $('#errorModal').modal();
                    $('#errorModal').on('hidden.bs.modal', function(e) {
                        $(this).remove();
                        $('#modalWrapper').html();
                        $(modalId).hide();
                    });

                    $('#successModal').modal();
                    $('#successModal').on('hidden.bs.modal', function(e) {
                        $(this).remove();
                        $('#modalWrapper').html();
                        $(modalId).hide();
                    });

                    $.ajax({
                        type: "POST",
                        url: "/contact",
                        data: formData,
                        dataType: "text",
                        xhrFields: {
                            withCredentials: true
                        },
                        beforeSend: function() {
                            $('#section-content').html(templateSpinner());
                        },
                        complete: function() {
                            $('#section-content').html(template());
                        },
                        success: function(response) {
                            var data = $.parseJSON(response)
                            if (data.status == 'success') {
                                $('#modalWrapper').html(templateSuccess(data));
                                $('#successModal').modal('show');
                            } else {
                                $('#modalWrapper').html(templateError(data.message));
                                $('#errorModal').modal('show');
                            }

                        },
                        error: function(jqXHR, exception) {
                            var msg = {
                                'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception
                            };
                            //$('#page').html(templateError(msg));
                            alert(msg);
                        }
                    });

                    event.preventDefault();
                });
            }
        }
    });
