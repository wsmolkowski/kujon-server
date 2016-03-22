define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html',
    'text!templates/error.html', 'datatables','text!templates/modal_lecturer.html'],
    function($, Handlebars, main, tplLecturers, tplError, datatables, tplModalLecturer) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tplLecturers);
            var templateError = Handlebars.compile(tplError);
            var templateModalLecturer = Handlebars.compile(tplModalLecturer);

            main.callLecturers(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    $('#lecturers-table').DataTable(main.getDataDatableConfig());

                    bindModals();
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }
            });

            function bindModals(){

                $('.lecturer-btn').click(function(){
                    var lecturerId = $(this).attr("data-lecturerId");
                    var modalId = '#lecturerModal' + lecturerId;

                    $(modalId).modal();

                    main.callLecturerDetails(lecturerId, function(lecturerInfo){
                        if (lecturerInfo.status == 'success'){

                            lecturerInfo.data['lecturer_id'] = lecturerId;
                            var htmlModal = templateModalLecturer(lecturerInfo.data);

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

            };
        }
    }    
});