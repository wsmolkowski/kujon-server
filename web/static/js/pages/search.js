define(['jquery', 'handlebars', 'main', 'text!templates/search.html',
        'text!templates/search_error.html', 'text!templates/modal_lecturer.html',
        'text!templates/modal_user.html', 'text!templates/spinner.html',
        'text!templates/search_results.html', 'text!templates/modal_lecturer.html',
        'text!templates/modal_course.html'
    ],
    function($, Handlebars, main, tpl, tplError, tplModalLecturer, tplModalUser, spinnerTpl, resultsTpl, lecturerTpl, courseTpl) {
        'use strict';
        return {
            render: function() {
                var template = Handlebars.compile(tpl);
                var templateError = Handlebars.compile(tplError);
                var templateModalLecturer = Handlebars.compile(tplModalLecturer);
                var templateModalUser = Handlebars.compile(tplModalUser);
                var templateSpinner = Handlebars.compile(spinnerTpl);
                var templateResults = Handlebars.compile(resultsTpl);
                var templateLecturer = Handlebars.compile(lecturerTpl);
                var templateCourse = Handlebars.compile(courseTpl);

                main.init();

                $('#section-content').html(template());

                $("#searchText").on("change paste keyup", function() {
                  $('#search_warning').empty();
                  $('#search_results').empty();
                });

                $('#searchSubmit').click(function() {

                    if ($('#searchText').val().length < 4) {
                        $('#searchText').focus();
                        $('#search_warning').html(
                            '<div class="alert alert-warning alert-dismissible fade in" role="alert">' +
                            '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                            'Wprowadź minimum 4 znaki.' +
                            '</div>'
                        );
                        return;
                    }

                    if ($('#searchText').val().length > 30) {
                        $('#searchText').focus();
                        $('#search_warning').html(
                            '<div class="alert alert-warning alert-dismissible fade in" role="alert">' +
                            '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
                            'Maksymalna długość frazy wynosi 30 znaków.' +
                            '</div>'
                        );
                        return;
                    }

                    $('#search_results').empty();

                    event.preventDefault();

                    var searchUrl = "/search/" + $('#searchType').val() + '/' + $('#searchText').val();

                    $('#search_results').html(templateSpinner);

                    main.ajaxGet(searchUrl).then(function(data) {
                        $("#searchText").empty();
                        
                        if (data.status == 'success') {
                            processResponse(data.data);
                            bindListeners();
                        } else {
                            $('#search_results').html(templateError({
                                'message': data.message
                            }));
                        }
                    });
                });

                function processResponse(response) {
                    $('#search_results').html(templateResults(response));
                    $('#table-results').DataTable(main.getDataTableConfig());
                }

                function bindListeners() {
                    $('#errorModal').modal();

                    $('#table-results').on('click', '.lecturer-btn', function() {
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
                                lecturerInfo.data.lecturer_id = lecturerId;
                                $('#modalWrapper').html(templateModalLecturer(lecturerInfo.data));
                                $(modalId).modal('show');
                            } else {
                                $('#modalWrapper').html(templateError(lecturerInfo));
                                $('#errorModal').modal('show');
                            }
                        });
                    });

                    $('#table-results').on('click', '.course-btn', function() {
                        var courseId = $(this).attr("data-courseId");
                        var modalId = '#courseModal' + courseId;

                        $(modalId).modal();
                        $(modalId).on('hidden.bs.modal', function(e) {
                            $(this).remove();
                            $('#modalWrapper').html();
                            $(modalId).hide();
                        });

                        main.ajaxGet('/courses/' + courseId).then(function(courseData) {
                            if (courseData.status == 'success') {
                                courseData.data.courseId = courseId;
                                $('#modalWrapper').html(templateCourse(courseData.data));
                                $(modalId).modal('show');
                            } else {
                                $('#modalWrapper').html(templateError(courseData));
                                $('#errorModal').modal('show');
                            }
                        });
                    });
                }
            }
        }
    });
