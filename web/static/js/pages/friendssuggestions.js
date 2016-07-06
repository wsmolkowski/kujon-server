define(['jquery', 'handlebars', 'main', 'text!templates/friendssuggestions.html', 'text!templates/error.html'],
    function($, Handlebars, main, tpl, tplError) {
        'use strict';

        return {
            render: function() {
                var template = Handlebars.compile(tpl);
                var templateError = Handlebars.compile(tplError);

                var request_url = main.getApiUrl('/friends/suggestions/');

                main.ajaxGet('/api/friends/suggestions/').then(function(data){
                  if (data.status == 'success') {
                      $('#section-content').html(template(data));
                  } else {
                      $('#section-content').html(templateError({
                          'message': data.data
                      }));
                  }
                });
            }
        }
    });
