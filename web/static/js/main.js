define("main", ["jquery", "handlebars", "text!templates/error.html"], function($, Handlebars, tplError)
{
        /* variables */

        var templateError = Handlebars.compile(tplError);
        var apiUrl = $('#api_url').val();
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

        function buildApiUrl(api){
            return apiUrl + api;
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

        function friendssuggestion(callback){
            callAjaxGet(buildApiUrl('/friends/suggestions'), callback);
        };

        function friends(callback){
            callAjaxGet(buildApiUrl('/friends'), callback);
        };

        function users(callback){
            callAjaxGet(buildApiUrl('/users'), callback);
        };

        function userInfo(userId, callback){
            var request_url = buildApiUrl('/users/') + userId;
            callAjaxGet(request_url, callback);
        };

        function terms(callback){
            callAjaxGet(buildApiUrl('/terms'), callback);
        };

        function faculties(callback){
            callAjaxGet(buildApiUrl('/faculties'), callback);
        };

        function programmes(callback){
            callAjaxGet(buildApiUrl('/programmes'), callback);
        };

        function grades(callback){
            callAjaxGet(buildApiUrl('/grades'), callback);
        };

        function courseseditions(callback){
            callAjaxGet(buildApiUrl('/courseseditions'), callback);
        };

        function lecturers(callback){
            callAjaxGet(buildApiUrl('/lecturers'), callback);
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
            },
            getConfig: function(){
                return config;
            },
            applicationConfig: function(){
                return applicationConfig;
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
            callFaculties: function(callback){
                faculties(callback);
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
            callTT: function(start, callback){
                TT(start, callback);
            },
            showSpinner: function(){
                showSpinner();
            },
            hideSpinner: function(){
                hideSpinner();
            },
            getApiUrl: function(){
                return apiUrl;l
            },
        };

});
