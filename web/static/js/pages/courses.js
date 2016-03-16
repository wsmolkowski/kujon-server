define(['jquery', 'handlebars', 'main', 'text!templates/courses.html', 'text!templates/course_details.html',
        'text!templates/error.html', 'text!templates/lecturer_details.html', 'text!templates/user_details.html',
        'text!templates/modal_lecturer.html', 'text!templates/modal_user.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError, tplLecturerDetails, tplUserDetails, tplModalLecturer, tplModalUser) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);
            var templateError = Handlebars.compile(tplError);
            var templateLecturerDetails = Handlebars.compile(tplLecturerDetails);
            var templateUserDetails = Handlebars.compile(tplUserDetails);
            var templateModalLecturer = Handlebars.compile(tplModalLecturer);
            var templateModalUser = Handlebars.compile(tplModalUser);


            main.callCourseseditions(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    bindListeners();
                } else {
                    $('#page').html(templateError(data));
                }
            });

            function bindListeners(){
                $('a.panel-row').bind( 'click', function(){
                    var courseId = $(this).attr("course-id");
                    var termId = $(this).attr("term-id");

                    if ($(this).attr("aria-expanded") == "false") {
                        $(this).attr("aria-expanded","true");

                        main.callCourseEditionDetails(courseId, termId, function(courseInfo){
                            var idContent = '#courseDetails' + courseId;

                            if (courseInfo.status == 'success'){
                                $(idContent).html(templateDetails(courseInfo.data));
                                bindModals();
                            } else {
                                $(idContent).html(templateError({'message': courseInfo.message}));
                            }

                        });


                        $('#details').on('show', function() {
                            $('#details-switch').html('Ukryj szczegóły')
                        })
                        $('#details').on('hide', function() {
                            $('#details-switch.collapsed').html('Pokaż szczegóły')
                        })

                    } else {
                        $(this).attr("aria-expanded","false");
                    }
                })
            };

            function bindModals(){
                $('.lecturer-btn').click(function(){
                    var lecturerId = $(this).attr("data-lecturerId");
                    var modalId = '#lecturerModal' + lecturerId;
                    var modalBodyId = '#lecturerBody' + lecturerId;

                    $(modalId).modal();

                    main.callLecturerDetails(lecturerId, function(lecturerInfo){
                        if (lecturerInfo.status == 'success'){

                            var htmlModal = templateModalLecturer({
                                'lecturer_id': lecturerId,
                                'title': lecturerInfo.data['first_name'] + ' ' + lecturerInfo.data['last_name']
                            });

                            $('#idLecturerModal').html(htmlModal);

                            $(modalId).modal('show');
                            $(modalBodyId).html(templateLecturerDetails(lecturerInfo.data));

                            $(modalId).on('hidden.bs.modal', function (e) {
                                $(this).remove();
                                $('#idLecturerModal').html();
                                $(modalId).hide();
                            });

                        } else {
                            $(modalId).modal('show');
                            $(modalBodyId).html(templateError({'message': userInfo.message}));
                        }
                    });

                });

                $('.user-btn').click(function(){
                    var userId = $(this).attr("data-userId");
                    var modalId = '#userModal' + userId;
                    var modalBodyId = '#userBody' + userId;

                    $(modalId).modal();

                    main.callUserInfo(userId, function(userInfo){
                        if (userInfo.status == 'success'){

                            var htmlModal = templateModalUser({
                                'user_id': userId,
                                'title': userInfo.data['first_name'] + ' ' + userInfo.data['last_name']
                            });

                            $('#idUserModal').html(htmlModal);
                            $(modalId).modal('show');

                            $(modalBodyId).html(templateUserDetails(userInfo.data));

                            $(modalId).on('hidden.bs.modal', function (e) {
                                $(this).remove();
                                $('#idUserModal').html();
                                $(modalId).hide();
                            });

                        } else {
                            $(modalId).modal('show');
                            $(modalBodyId).html(templateError({'message': userInfo.message}));
                        }
                    });

                });
            }
        }
    }    
});