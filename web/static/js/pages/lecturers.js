define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html',
    'text!templates/error.html', 'text!templates/modal_lecturer.html', 'text!templates/modal_error.html'],
    function($, Handlebars, main, tplLecturers, tplError, tplModalLecturer, tplModalError) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tplLecturers);
            var templateError = Handlebars.compile(tplError);
            var templateModalLecturer = Handlebars.compile(tplModalLecturer);
            var templateModalError = Handlebars.compile(tplModalError);

            main.callLecturers(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                    bindModals();
                } else {
                    $('#section-content').html(templateError({'message': data.message}));
                }
            });

            function bindModals(){

                $('.lecturer-btn').click(function(){
                    var lecturerId = $(this).attr("data-lecturerId");
                    var modalId = '#lecturerModal' + lecturerId;
                    $('#errorModal').modal();

                    $(modalId).modal();
                    $(modalId).on('hidden.bs.modal', function (e) {
                        $(this).remove();
                        $('#modalWrapper').html();
                        $(modalId).hide();
                    });

                    main.callLecturerDetails(lecturerId, function(lecturerInfo){
                        if (lecturerInfo.status == 'success'){

                            lecturerInfo.data['lecturer_id'] = lecturerId;

                            $('#modalWrapper').html(templateModalLecturer(lecturerInfo.data));

                            $(modalId).modal('show');

                        } else {
                            $('#modalWrapper').html(templateModalError(lecturerInfo));

                            $('#errorModal').modal('show');
                        }
                    });

                });

            };
        }
    }    
});