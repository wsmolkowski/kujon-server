define(['jquery', 'handlebars', 'main', 'text!templates/theses.html', 'text!templates/error.html', 'text!templates/modal_lecturer.html', 'text!templates/modal_user.html'],
    function($, Handlebars, main, tpl, tplError, tplModalLecturer, tplModalUser) {
        'use strict';
        return {
            render: function() {
                var template = Handlebars.compile(tpl);
                var templateError = Handlebars.compile(tplError);
                var templateModalLecturer = Handlebars.compile(tplModalLecturer);
                var templateModalUser = Handlebars.compile(tplModalUser);

                main.ajaxGet('/theses').then(function(data) {
                    if (data.status == 'success') {
                        $('#section-content').html(template(data));
                        $('#table-faculties').DataTable(main.getDataTableConfig());

                        bindListeners();
                    } else {
                        $('#section-content').html(templateError({
                            'message': data.message
                        }));
                    }
                });

                function bindListeners() {
                    $('#errorModal').modal();

                    $('.description-lecturer').click(function() {
                        var lecturerId = $(this).attr("data-lecturerId");
                        var modalId = '#lecturerModal' + lecturerId;

                        $(modalId).modal();
                        $(modalId).on('hidden.bs.modal', function(e) {
                            $(this).remove();
                            $('#modalWrapper').html();
                            $(modalId).hide();
                        });

                        main.ajaxGet('/lecturers/' + lecturerId).then(function(lecturerInfo) {
                            if (lecturerInfo.status == 'success') {
                                lecturerInfo.data['lecturer_id'] = lecturerId;
                                $('#modalWrapper').html(templateModalLecturer(lecturerInfo.data));
                                $(modalId).modal('show');
                            } else {
                                $('#modalWrapper').html(templateModalError(lecturerInfo));
                                $('#errorModal').modal('show');
                            }
                        });

                    });

                    $('.description-user').click(function() {
                        var userId = $(this).attr("data-userId");
                        var modalId = '#userModal' + userId;

                        $(modalId).modal();

                        main.ajaxGet('/users/' + userId).then(function(userInfo) {
                            if (userInfo.status == 'success') {
                                userInfo.data['user_id'] = userId;
                                $('#modalWrapper').html(templateModalUser(userInfo.data));

                                $(modalId).on('hidden.bs.modal', function(e) {
                                    $(this).remove();
                                    $('#modalWrapper').html();
                                    $(modalId).hide();
                                });
                                $(modalId).modal('show');
                            } else {
                                $('#modalWrapper').html(templateModalError(userInfo));
                                $('#errorModal').modal('show');
                            }
                        });
                    });
                }
            }
        }
    });
