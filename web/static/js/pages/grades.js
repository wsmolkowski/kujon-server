define(['jquery', 'handlebars', 'main', 'text!templates/grades.html',
'text!templates/error.html', 'text!templates/modal_course.html', 'text!templates/modal_error.html'],
    function($, Handlebars, main, tpl, tplError, tplCourseModal, tplModalError) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);
            var templateCourseModal = Handlebars.compile(tplCourseModal);
            var templateModalError = Handlebars.compile(tplModalError);

            main.init();

            main.ajaxGet('/grades').then(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                    $('#table-grades').DataTable(main.getDataTableConfig());

                    bindModals();
                } else {
                    $('#section-content').html(templateError({'message': data.message}));
                }
            });

            function bindModals(){
                $('.courses-modal').click(function(){
                    var courseId = $(this).attr("data-courseId");
                    var termId = $(this).attr("data-termId");
                    var modalId = '#courseModal' + courseId;
                    $('#errorModal').modal();

                    $(modalId).modal();
                    $(modalId).on('hidden.bs.modal', function (e) {
                        $(this).remove();
                        $('#modalWrapper').html();
                        $(modalId).hide();
                    });

                    var url = '/courseseditions/' + courseId + '/' + encodeURIComponent(termId);
                    main.ajaxGet(url).then(function(courseInfo){
                        if (courseInfo.status == 'success'){
                            courseInfo.data['courseId'] = courseId;
                            $('#modalWrapper').html(templateCourseModal(courseInfo.data));
                            $(modalId).modal('show');
                        } else {
                            $('#modalWrapper').html(templateModalError(courseInfo));
                            $('#errorModal').modal('show');
                        }
                    });
                });
            }
        }
    }    
});