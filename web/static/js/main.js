define("main", ["jquery", "handlebars", "text!templates/error.html", 'jquery-cookie'], function($, Handlebars, tplError, jc)
{
        /* variables */
        var templateError = Handlebars.compile(tplError);
        var config;


        function updateConfig(data){
            config = data;
        }

        var spinner = 0;

        /* private methods */

        function showSpinner(){
            if (spinner < 1){
                $('#spinner').show();
                spinner ++;
            }
        }

        function hideSpinner(){
            if (spinner > 0){
                $('#spinner').hide();
                spinner = spinner - 1;
            }
        }

        function buildConfig(){
            return $.ajax({
                    type: 'GET',
                    url: 'https://api.kujon.mobi/config',
                    dataType: "json",
                    xhrFields: {
                      withCredentials: true
                    },
                    success:  function (data) {
                      if (data.status == 'success'){
                        updateConfig(data.data);

                      } else {
                        $('#page').html(templateError(data));
                      }
                    },
                    error: function(jqXHR, exception) {
                      var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception};
                      $('#page').html(templateError(msg));
                    }
                });
        };

        function buildApiUrl(api){
            return config['API_URL'] + api;
        };

        function buildWebUrl(url){
            return config['DEPLOY_URL'] + url;
        };

        function callAjaxPost(request_url, jsonData, callback){

            $.ajax({
                type: 'POST',
                url: request_url,
                data: JSON.stringify(jsonData),
                //contentType: "application/json",
                dataType: "json",
                xhrFields: {
                    withCredentials: true
                },
                beforeSend: function(){
                    showSpinner();
                },
                complete: function(){
                    hideSpinner();
                },
                crossDomain: true,
                success:  function (data) {
                    callback(data);
                },
                error: function(jqXHR, exception) {
                    var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception};
                    $('#page').html(templateError(msg));
                }
            });
        };

        function callAjaxGet(request_url, callback){

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
                },
                beforeSend: function(){
                    showSpinner();
                },
                complete: function(){
                    hideSpinner();
                },
                crossDomain: true,
                success:  function (data) {
                    callback(data);
                },
                error: function(jqXHR, exception) {
                    var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception};
                    $('#page').html(templateError(msg));
                }
            });
        };

        function usoses(callback){
            callAjaxGet(buildApiUrl('/usoses'), callback);
        };

        function friendssuggestion(callback){
            callAjaxGet(buildApiUrl('/friends/suggestions/'), callback);
        };

        function friends(callback){
            callAjaxGet(buildApiUrl('/friends/'), callback);
        };

        function users(callback){
            callAjaxGet(buildApiUrl('/users/'), callback);
        };

        function userInfo(userId, callback){
            var request_url = buildApiUrl('/users/') + userId;
            callAjaxGet(request_url, callback);
        };

        function terms(callback){
            callAjaxGet(buildApiUrl('/terms/'), callback);
        };

        function programmes(callback){
            callAjaxGet(buildApiUrl('/programmes/'), callback);
        };

        function grades(callback){
            callAjaxGet(buildApiUrl('/grades/'), callback);
        };

        function courseseditions(callback){
            callAjaxGet(buildApiUrl('/courseseditions/'), callback);
        };

        function lecturers(callback){
            callAjaxGet(buildApiUrl('/lecturers/'), callback);
        };

        function lecturerDetails(lecturerId, callback){
            var request_url = buildApiUrl('/lecturers/') + lecturerId;
            callAjaxGet(request_url, callback);
        };

        function courseEditionDetails(courseId, termId, callback){
            var request_url = buildApiUrl('/courseseditions/') + courseId + '/' + encodeURIComponent(termId);
            callAjaxGet(request_url, callback);
        };

        function TT(start, callback) {
            var request_url = buildApiUrl('/tt/') + start;
            callAjaxGet(request_url, callback);
        };

        function registerUsos(usosId){
            var url = buildApiUrl('/authentication/register');
            var data = {
                'usos_id': usosId
            }

            callAjaxPost(url, data, function(response){
                if (response.status == 'success' && response.data.redirect !== undefined){
                    window.location.href = response.data.redirect;
                } else {
                    $('#page').html(templateError(response));
                }
            });
        }

        /* public methods */
        return {

            init: function() {

                // {{#nl2br}} replace returns with <br>
                Handlebars.registerHelper('nl2br', function(text) {
                    text = Handlebars.Utils.escapeExpression(text);
                    var nl2br = (text + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + '<br>' + '$2');
                    return new Handlebars.SafeString(nl2br);
                });

                // {{#replace}} replace string handlebar helper
                 Handlebars.registerHelper('replspechars', function( string ){
	                var pom= ( string || '' ).replace( "(", "\\(" );
	                pom = ( pom || '' ).replace( ")", "\\)" );
	                pom = ( pom || '' ).replace( "`", "\\`" );
	                return pom;
                });

                return buildConfig();
            },
            getConfig: function(){
                return config;
            },
            callUsoses: function(callback){
                usoses(callback);
            },
            callFriendsSuggestion: function(callback){
                friendssuggestion(callback);
            },
            callFriends: function(callback){
                friends(callback);
            },
            callUsers: function(callback){
                users(callback);
            },
            callUserInfo: function(userId, callback){
                userInfo(userId, callback);
            },
            callTerms: function(callback){
                terms(callback);
            },
            callProgrammes: function(callback){
                programmes(callback);
            },
            callGrades: function(callback){
                grades(callback);
            },
            callCourseseditions: function(callback){
                courseseditions(callback);
            },
            callCourseEditionDetails: function(courseId, termId, callback){
                courseEditionDetails(courseId, termId, callback);
            },
            callLecturers: function(callback){
                lecturers(callback);
            },
            callLecturerDetails: function(lecturerId, callback){
                lecturerDetails(lecturerId, callback);
            },
            isUserLoggedIn: function(){
                if (! $.cookie('USER_SECURE_COOKIE')){
                    return false;
                } else {
                    return true;
                }
            },
            isUserRegistered: function(){
                return config['USOS_PAIRED'];
            },
            callTT: function(start, callback){
                TT(start, callback);
            },
            showSpinner: function(){
                showSpinner();
            },
            hideSpinner: function(){
                hideSpinner();
            },
            callRegisterUsos: function(usosId){
                registerUsos(usosId);
            },
            getDatableConfig: function(){
                return {
                    paging: false,
                    "language": {
                        "decimal":        "",
                        "emptyTable":     "Brak danych do wyświetlenia",
                        "info":           "_START_ do _END_ z _TOTAL_ wierszy",
                        "infoEmpty":      "0 do 0 z 0 wierszy",
                        "infoFiltered":   "(filtered from _MAX_ total entries)",
                        "infoPostFix":    "",
                        "thousands":      ",",
                        "lengthMenu":     "Pokaż _MENU_ wierszy",
                        "loadingRecords": "Wszytuję...",
                        "processing":     "Przetwarzam...",
                        "search":         "Szukaj:",
                        "zeroRecords":    "Nie znaleziono rekordów",
                        "paginate": {
                            "first":      "Pierwszy",
                            "last":       "Ostatni",
                            "next":       "Następny",
                            "previous":   "Poprzedni"
                        },
                        "aria": {
                            "sortAscending":  ": activate to sort column ascending",
                            "sortDescending": ": activate to sort column descending"
                        }
                    }
                };
            }
        };

});
