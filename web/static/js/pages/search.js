define(['jquery', 'handlebars', 'main', 'text!templates/search.html',
        'text!templates/search_error.html', 'text!templates/modal_lecturer.html',
        'text!templates/modal_user.html', 'text!templates/spinner.html',
        'text!templates/results.html'
    ],
    function($, Handlebars, main, tpl, tplError, tplModalLecturer, tplModalUser
        , spinnerTpl, resultsTpl) {
        'use strict';
        return {
            render: function() {
                var template = Handlebars.compile(tpl);
                var templateError = Handlebars.compile(tplError);
                var templateModalLecturer = Handlebars.compile(tplModalLecturer);
                var templateModalUser = Handlebars.compile(tplModalUser);
                var templateSpinner = Handlebars.compile(spinnerTpl);
                var templateResults = Handlebars.compile(resultsTpl);

                $('#section-content').html(template());

                $('#searchSubmit').click(function() {
                    var searchUrl = "/search/" + $('#searchType').val() + '/' + $('#searchText').val();

                    $('#search_results').html(templateSpinner);

                    main.ajaxGet(searchUrl).then(function(data) {
                        if (data.status == 'success') {
                            processResponse(data.data);
                        } else {
                            $('#search_results').html(templateError({
                                'message': data.message
                            }));
                        }
                    });

                    event.preventDefault();
                });

                function processResponse(response) {
                    $('#searchText').val("");

                    switch ($('#searchType').val()) {
                        case 'users':
                            $('#search_results').html(templateResults(response));
                            break;
                        case 'courses':
                            $('#search_results').html(templateResults(response));
                            break;
                        case 'faculties':
                            $('#search_results').html(templateResults(response));
                            break;
                        case 'programmes':
                            $('#search_results').html(templateResults(response));
                            break;
                    }

                    $('#table-results').DataTable(main.getDataTableConfig());
                }


                /*
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
                */

            }
        }
    });
