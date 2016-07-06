define(['jquery', 'handlebars', 'main', 'text!templates/crstests.html', 'text!templates/error.html', 'text!templates/modal_course.html', 'text!templates/modal_error.html', 'text!templates/modal_crstest.html'],
    function($, Handlebars, main, tpl, tplError, tplCourseModal, tplModalError, tplModalScrTest) {
        'use strict';
        return {
            render: function() {
                var template = Handlebars.compile(tpl);
                var templateError = Handlebars.compile(tplError);
                var templateCourseModal = Handlebars.compile(tplCourseModal);
                var templateModalError = Handlebars.compile(tplModalError);
                var templateModalScrTest = Handlebars.compile(tplModalScrTest);

                main.init();

                main.ajaxGet('/crstests').then(function(data) {
                    if (data.status == 'success') {
                        $('#section-content').html(template(data.data));
                        $('#table-crstests').DataTable(main.getDataTableConfig());

                        bindModals();

                    } else {
                        $('#section-content').html(templateError({
                            'message': data.message
                        }));
                    }
                });

                function bindModals(){
                  $('#table-crstests').on('click', '.courses-modal', function(){
                      var courseId = $(this).attr("data-courseId");
                      var termId = $(this).attr("data-termId");
                      var modalId = '#courseModal' + courseId;
                      $('#errorModal').modal();

                      $(modalId).modal();

                      var url = '/courseseditions/' + courseId + '/' + encodeURIComponent(termId);
                      main.ajaxGet(url).then(function(courseInfo){
                          if (courseInfo.status == 'success'){
                              courseInfo.data['courseId'] = courseId;
                              $('#modalWrapper').html(templateCourseModal(courseInfo.data));
                              $(modalId).modal('show');
                              $(modalId).on('hidden.bs.modal', function (e) {
                                  $(this).remove();
                                  $('#modalWrapper').html();
                                  $(modalId).hide();
                              });
                          } else {
                              $('#modalWrapper').html(templateModalError(courseInfo));
                              $('#errorModal').on('hidden.bs.modal', function (e) {
                                  $(this).remove();
                                  $('#modalWrapper').html();
                                  $(modalId).hide();
                              });
                              $('#errorModal').modal('show');
                          }
                      });
                  });

                  $('#table-crstests').on('click', '.crstest-modal', function(){
                      var nodeId = $(this).attr("data-nodeId");
                      var modalId = '#cststestModal' + nodeId;
                      $('#errorModal').modal();

                      $(modalId).modal();

                      var url = '/crstests/' + nodeId;
                      main.ajaxGet(url).then(function(crstest){
                          if (crstest.status == 'success'){
                              $('#modalWrapper').html(templateModalScrTest(crstest.data));
                              $(modalId).modal('show');
                              $(modalId).on('hidden.bs.modal', function (e) {
                                  $(this).remove();
                                  $('#modalWrapper').html();
                                  $(modalId).hide();
                              });
                          } else {
                              $('#modalWrapper').html(templateModalError(crstest));
                              $('#errorModal').on('hidden.bs.modal', function (e) {
                                  $(this).remove();
                                  $('#modalWrapper').html();
                                  $(modalId).hide();
                              });
                              $('#errorModal').modal('show');
                          }
                      });
                  });

                }
            }
        }
    });
