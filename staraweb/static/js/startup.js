define(['main', 'static/js/router.js', 'jquery', 'jquery-cookie'], function(main, router, $, jc) {
    main.init();

    $(document).ready(function(){
        $( window ).unload(function() {
            main.cleanSecureCookie();
        });
    });

});
