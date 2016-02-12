define("main", ["jquery", ], function($) {

        var getConfig = function(){
            $.ajax({
                    type: 'GET',
                    url: 'http://localhost:8888/config',
                    success:  function (data) {
                        return data;
                    },
                    error: function (err) {
                        console.log(err);
                    }
                });
        };

        //var config = getConfig();
        var config = {"USOS_API": "http://localhost:8881"};

        return {
            getConfig: function() {
                return config;
            }
        };


});
