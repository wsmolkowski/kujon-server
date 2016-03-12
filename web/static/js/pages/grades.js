define(['jquery', 'handlebars', 'main', 'text!templates/grades.html', 'text!templates/error.html', 'text!templates/course_details.html'],
function($, Handlebars, main, tpl, tplError, tplCourse) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);
            var templateCourse = Handlebars.compile(tplCourse);

            main.callGrades(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }

                $('#courseModal').on('show.bs.modal', function (event) {
                      var button = $(event.relatedTarget) // Button that triggered the modal
                      var courseId = button.attr('data-courseId') // Extract info from data-* attributes
                      var termId = button.attr('data-termId') // Extract info from data-* attributes

                      // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
                      // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.


                      var modal = $(this)

                      main.callCourseEditionDetails(courseId, termId, function(courseInfo){
                        if (courseInfo.status == 'success'){
                            modal.find('.modal-title').text('Informacje o kursie ' + courseId + ' w semestrze ' + termId);
                            modal.find('.modal-body').html(templateCourse(courseInfo.data));
                        } else {
                            modal.find('.modal-body').html(templateError({'message': courseInfo.message}));
                        }
                      });
                });
            });

            //a tutaj możesz np. zapiąć listenery

        }
    }    
});