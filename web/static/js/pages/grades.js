define(['jquery', 'handlebars', 'main', 'text!templates/grades.html', 'text!templates/error.html', 'text!templates/modal_course.html', 'datatables'],
    function($, Handlebars, main, tpl, tplError, tplCourseModal, datatables) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);
            var templateCourseModal = Handlebars.compile(tplCourseModal);

            main.callGrades(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    bindModals();
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }
            });

            function bindModals(){
                $('.course-btn').click(function(){
                    var courseId = $(this).attr("data-courseId");
                    var termId = $(this).attr("data-termId");
                    var modalId = '#courseModal' + courseId;

                    $(modalId).modal();

                    main.callCourseEditionDetails(courseId, termId, function(courseInfo){
                        if (courseInfo.status == 'success'){
                            courseInfo.data['courseId'] = courseId;
                            var htmlModal = templateCourseModal(courseInfo.data);

                            $('#modalWrapper').html(htmlModal);

                            $(modalId).modal('show');

                            $(modalId).on('hidden.bs.modal', function (e) {
                                $(this).remove();
                                $('#modalWrapper').html();
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