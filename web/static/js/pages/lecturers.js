define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html', 'text!templates/lecturer_details.html',
    'text!templates/error.html', 'text!templates/course_details_modal.html', 'datatables','text!templates/modal_lecturer.html',
    'text!templates/lecturer_details.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError, tplCourseModal, datatables, tplModalLecturer, tplLecturerDetails) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);
            var templateCourse = Handlebars.compile(tplCourseModal);
            var templateError = Handlebars.compile(tplError);
            var templateModalLecturer = Handlebars.compile(tplModalLecturer);
            var templateLecturerDetails = Handlebars.compile(tplLecturerDetails);

            main.callLecturers(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    $('#lecturers-table').DataTable();

                    bindModals();
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }
            });


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

                            $('#modalWrapper').html(htmlModal);

                            $(modalId).modal('show');
                            $(modalBodyId).html(templateLecturerDetails(lecturerInfo.data));

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

            };
        }
    }    
});