define(['jquery', 'handlebars', 'main', 'nice-select', 'easing', 'bootstrap-table', 'text!templates/courses.html', 'text!templates/course_details.html',
        'text!templates/error.html', 'text!templates/modal_lecturer.html', 'text!templates/modal_user.html',
         'text!templates/modal_error.html'],
    function($, Handlebars, main, nice, easing, bootstrapTable, tpl, tplDetails, tplError, tplModalLecturer, tplModalUser, tplModalError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);
            var templateError = Handlebars.compile(tplError);
            var templateModalLecturer = Handlebars.compile(tplModalLecturer);
            var templateModalUser = Handlebars.compile(tplModalUser);
            var templateModalError = Handlebars.compile(tplModalError);

            slide();

            main.callCourseseditions(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                    slide();
                    // bindListeners();
                } else {
                    $('#section-content').html(templateError(data));
                }
            });

            function slide(){
                $('select').niceSelect({
                    placeholder: 'Wybierz'
                });

                var $table = $('#myTable');

                $table.on('expand-row.bs.table', function (e, index, row, $detail) {
                    var res = $("#" + row._data.details).html();
                    $detail.html(res);
                });

                $table.on("click-row.bs.table", function(e, row, $tr) {
                    // In my real scenarion, trigger expands row with text detailFormatter..
                    //$tr.find(">td>.detail-icon").trigger("click");
                    $tr.find(">td>.detail-icon").triggerHandler("click");
                });

            }

            function bindListeners(){
                $('a.panel-row').bind( 'click', function(){
                    var courseId = $(this).attr("course-id");
                    var termId = $(this).attr("term-id");

                    if ($(this).attr("aria-expanded") == "false") {
                        $(this).attr("aria-expanded","true");

                        // escape special chars for courseId that are escaped in helper {{replspechars}}
                        var courseId_notescaped= ( courseId || '' ).replace( "\\(", "(" );
	                    courseId_notescaped = ( courseId_notescaped || '' ).replace( "\\)", ")" );
	                    courseId_notescaped = ( courseId_notescaped || '' ).replace( "\\`", "`" );

                        main.callCourseEditionDetails(courseId_notescaped, termId, function(courseInfo){
                            var idContent = '#courseDetails' + courseId;

                            if (courseInfo.status == 'success'){
                                $(idContent).html(templateDetails(courseInfo.data));
                                bindModals();
                            } else {
                                $(idContent).html(templateError({'message': courseInfo.message}));
                            }

                        });

                    } else {
                        $(this).attr("aria-expanded","false");
                    }
                })
            };

            function bindModals(){
                $('#errorModal').modal();

                $('.lecturer-btn').click(function(){
                    var lecturerId = $(this).attr("data-lecturerId");
                    var modalId = '#lecturerModal' + lecturerId;

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

                $('.user-btn').click(function(){
                    var userId = $(this).attr("data-userId");
                    var modalId = '#userModal' + userId;
                    var modalBodyId = '#userBody' + userId;

                    $(modalId).modal();

                    $(modalId).on('hidden.bs.modal', function (e) {
                        $(this).remove();
                        $('#modalWrapper').html();
                        $(modalId).hide();
                    });

                    main.callUserInfo(userId, function(userInfo){
                        if (userInfo.status == 'success'){

                            userInfo.data['user_id'] = userId;

                            $('#modalWrapper').html(templateModalUser(userInfo.data));
                            $(modalId).modal('show');
                        } else {
                            $('#modalWrapper').html(templateModalError(userInfo));
                            $('#errorModal').modal('show');
                        }
                    });
                });
            }

        }
    }    
});