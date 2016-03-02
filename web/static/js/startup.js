define(['main', 'static/js/router.js', 'jquery', 'navigation'], function(main, router, $, navigation) {
    main.init();

    navigation.render();

    $(document).ready(function(){
        $( window ).unload(function() {
            //main.cleanSecureCookie();

        });
    });

});
