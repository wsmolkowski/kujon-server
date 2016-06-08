define(['jquery', 'handlebars', 'main', 'text!templates/courses.html', 'text!templates/course_details.html',
        'text!templates/error.html', 'text!templates/modal_lecturer.html', 'text!templates/modal_user.html',
        'text!templates/modal_error.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError, tplModalLecturer, tplModalUser, tplModalError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);
            var templateError = Handlebars.compile(tplError);
            var templateModalLecturer = Handlebars.compile(tplModalLecturer);
            var templateModalUser = Handlebars.compile(tplModalUser);
            var templateModalError = Handlebars.compile(tplModalError);

            main.init();

            main.callCourseseditions(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                    bindListeners();

                } else {
                    $('#section-content').html(templateError(data));
                }
            });



            function bindListeners(){
                var table = $('#courses-table').DataTable(main.getDataTableConfig());


              // Add event listener for opening and closing details
              $('#courses-table').on('click', 'td.details-control', function () {
                    var courseId = $(this).attr("course-id");
                    var termId = $(this).attr("term-id");
                    var courseId_notescaped= ( courseId || '' ).replace( "\\(", "(" );

                    courseId_notescaped = ( courseId_notescaped || '' ).replace( "\\)", ")" );
                    courseId_notescaped = ( courseId_notescaped || '' ).replace( "\\`", "`" );

                    var tr = $(this).closest('tr');

                    main.callCourseEditionDetails(courseId_notescaped, termId, function(courseInfo){
                        var idContent = '#courseDetails' + courseId;

                        if (courseInfo.status == 'success'){

                              var row = table.row(tr);
                              if (row.child.isShown()) {
                                  // This row is already open - close it
                                  row.child.hide();
                                  tr.removeClass('shown');
                              } else {
                                  // Open this row
                                  row.child(templateDetails(courseInfo.data)).show();
                                  tr.addClass('shown');
                              }

                            //bindModals();
                        } else {
                            $(idContent).html(templateError({'message': courseInfo.message}));
                        }

                    });


              });

            };

            /*
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
            */
        }
    }    
});