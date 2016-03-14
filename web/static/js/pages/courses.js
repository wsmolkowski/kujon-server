define(['jquery', 'handlebars', 'main', 'text!templates/courses.html', 'text!templates/course_details.html',
        'text!templates/error.html', 'text!templates/lecturer_details.html', 'text!templates/user_details.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError, tplLecturerDetails, tplUserDetails) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);
            var templateError = Handlebars.compile(tplError);
            var templateLecturerDetails = Handlebars.compile(tplLecturerDetails);
            var templateUserDetails = Handlebars.compile(tplUserDetails);

            var API_URL;

            main.getConfig(function(config){
                API_URL = config['API_URL'];
            });

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
                    var ariaexpanded = $(this).attr("aria-expanded");

                    if (ariaexpanded == "false") {
                        $(this).attr("aria-expanded","true");

                        main.callCourseEditionDetails(courseId, termId, function(courseInfo){
                            var idContent = '#courseDetails' + courseId;

                            if (courseInfo.status == 'success'){
                                $(idContent).html(templateDetails(courseInfo.data));
                            } else {
                                $(idContent).html(templateError({'message': courseInfo.message}));
                            }

                            $('#lecturerModal').on('show.bs.modal', function (event) {
                                  var button = $(event.relatedTarget);
                                  var lecturerId = button.attr('data-lecturerId');

                                  var modal = $(this);

                                  main.callLecturerDetails(lecturerId, function(lecturerInfo){
                                    if (lecturerInfo.status == 'success'){
                                        lecturerInfo.data['API_URL'] = API_URL;
                                        modal.find('.modal-title').text(lecturerInfo.data['first_name'] + ' ' + lecturerInfo.data['last_name']);
                                        modal.find('.modal-body').html(templateLecturerDetails(lecturerInfo.data));
                                    } else {
                                        modal.find('.modal-body').html(templateError({'message': lecturerInfo.message}));
                                    }
                                  });
                            });

                            $('#userModal').on('show.bs.modal', function (event) {
                                  var button = $(event.relatedTarget);
                                  var userId = button.attr('data-userId');

                                  var modal = $(this);

                                  main.callUserInfo(userId, function(userInfo){
                                    if (userInfo.status == 'success'){
                                        userInfo.data['API_URL'] = API_URL;
                                        modal.find('.modal-title').text(userInfo.data['first_name'] + ' ' + userInfo.data['last_name']);
                                        modal.find('.modal-body').html(templateUserDetails(userInfo.data));
                                    } else {
                                        modal.find('.modal-body').html(templateError({'message': userInfo.message}));
                                    }
                                  });
                            });
                        });


                    } else {
                        $(this).attr("aria-expanded","false");
                    }
                })
            };

        }
    }    
});