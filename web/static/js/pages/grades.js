define(['jquery', 'handlebars', 'main', 'text!templates/grades.html', 'text!templates/error.html', 'text!templates/modal_course.html', 'datatables'],
    function($, Handlebars, main, tpl, tplError, tplCourseModal, datatables) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);
            var templateCourse = Handlebars.compile(tplCourseModal);

            main.callGrades(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }

                $('#grades-table').DataTable();

                $('#courseModal').on('show.bs.modal', function (event) {
                      var button = $(event.relatedTarget)
                      var courseId = button.attr('data-courseId')
                      var termId = button.attr('data-termId')

                      var modal = $(this)

                      main.callCourseEditionDetails(courseId, termId, function(courseInfo){
                        if (courseInfo.status == 'success'){
                            modal.find('.modal-title').text(courseInfo.data['name']);
                            modal.find('.modal-body').html(templateCourse(courseInfo.data));
                        } else {
                            modal.find('.modal-body').html(templateError({'message': courseInfo.message}));
                        }
                      });
                });
            });
        }
    }    
});