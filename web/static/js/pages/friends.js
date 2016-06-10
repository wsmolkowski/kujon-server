define(['jquery', 'handlebars', 'main', 'text!templates/friends.html',
        'text!templates/error.html', 'text!templates/modal_course.html', 'text!templates/modal_user.html'
    ],
    function($, Handlebars, main, tplFriends, tplError, tplCourseModal, tplModalUser) {
        'use strict';
        return {
            render: function() {
                var template = Handlebars.compile(tplFriends);
                var templateModalCourse = Handlebars.compile(tplCourseModal);
                var templateError = Handlebars.compile(tplError);
                var templateModalUser = Handlebars.compile(tplModalUser);

                main.ajaxGet('/friends/suggestions').then(function(data) {
                    if (data.status == 'success') {
                        $('#section-content').html(template(data.data));
                        $('#table-friends').DataTable(main.getDataTableConfig());
                        $('#table-find-friends').DataTable(main.getDataTableConfig());
                        bindModals();

                    } else {
                        $('#section-content').html(templateError({
                            'message': data.message
                        }));
                    }
                });

                function bindModals() {

                    $('.friends-btn').click(function() {
                        var friendId = $(this).attr("data-friendId");
                        var modalId = '#userModal' + friendId;

                        $(modalId).modal();

                        main.ajaxGet('/users/' + friendId).then(function(friendInfo) {
                            if (friendInfo.status == 'success') {
                                friendInfo.data['friend_id'] = friendId;
                                $('#modalWrapper').html(templateModalUser(friendInfo.data));
                                $(modalId).modal('show');

                                $(modalId).on('hidden.bs.modal', function(e) {
                                    $(this).remove();
                                    $('#modalWrapper').html();
                                    $(modalId).hide();
                                });

                            } else {
                                $(modalId).modal('show');
                                $(modalBodyId).html(templateError({
                                    'message': userInfo.message
                                }));
                            }
                        })
                    });
                }
            }
        }
    });
