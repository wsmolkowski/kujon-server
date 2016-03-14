define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html', 'text!templates/lecturer_details.html', 'text!templates/error.html', 'text!templates/course_details_modal.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError, tplCourseModal) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);
            var templateCourse = Handlebars.compile(tplCourseModal);
            var templateError = Handlebars.compile(tplError);

            main.callLecturers(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    bindListeners();
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }
            });

            var API_URL;
            main.getConfig(function(config){
                API_URL = config['API_URL'];
            });

            function bindListeners(){
                $('a.panel-row').bind( 'click', function(){
                    var lecturerId = $(this).attr("lecturer-id");
                    var ariaexpanded = $(this).attr("aria-expanded");
                    if (ariaexpanded == "false") {

                        $(this).attr("aria-expanded","true");

                        main.callLecturerDetails(lecturerId, function(lecturerInfo){
                            var idContent = '#lecturerDetails' + lecturerId;

                            if (lecturerInfo.status == 'success'){
                                lecturerInfo.data['API_URL'] = API_URL;
                                $(idContent).html(templateDetails(lecturerInfo.data));
                            } else {
                                $(idContent).html(templateError({'message': lecturerInfo.message}));
                            }

                            $('#courseModal').on('show.bs.modal', function (event) {
                                  var button = $(event.relatedTarget);
                                  var courseId = button.attr('data-courseId');
                                  var termId = button.attr('data-termId');
                                  var modal = $(this);

                                  main.callCourseEditionDetails(courseId, termId, function(courseInfo){
                                    if (courseInfo.status == 'success'){
                                        courseInfo.data['API_URL'] = API_URL;
                                        modal.find('.modal-title').text(courseInfo.data['course_name']);
                                        modal.find('.modal-body').html(templateLecturerDetails(courseInfo.data));
                                    } else {
                                        modal.find('.modal-body').html(templateError({'message': courseInfo.message}));
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