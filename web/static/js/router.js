define(['jquery','main','crossroads', 'hasher', 'bootstrap'], function(jquery, main, crossroads, hasher) {
'use strict';
    
    function setActiveLink(hash) {  
        //console.log(hash);
        
        //pokaż kręcacz porządnie
        $('#spinner').show();

        require(['lib/pages/'+hash], function(page) {
            page.render();

            $('.navbar li.active').removeClass('active'); //trochę gupio ale na szybko
            $('.navbar a[href="#'+hash+'"]').parent().addClass('active');
            
            //schowaj kręcacz (?)
            $('#spinner').hide();
        });
    }

    crossroads.addRoute('', function() {
        setActiveLink('home');
    });

    // "_=_" is added on callback from facebook - should be removed
    crossroads.addRoute('_=_', function() {
        setActiveLink('home');
    });

    crossroads.addRoute('home', function() {
        setActiveLink('home');
    });
    
    crossroads.addRoute('user', function() {
        setActiveLink('user');
    });

    crossroads.addRoute('grades', function() {
        setActiveLink('grades');
    });

    crossroads.addRoute('courses', function() {
        setActiveLink('courses');
    });

    crossroads.addRoute('terms', function() {
        setActiveLink('terms');
    });

    crossroads.addRoute('programmes', function() {
        setActiveLink('programmes');
    });

    crossroads.addRoute('lecturers', function() {
        setActiveLink('lecturers');
    });

    crossroads.addRoute('register', function() {
        setActiveLink('register');
    });

    crossroads.addRoute('about', function() {
        setActiveLink('about');
    });

    crossroads.addRoute('friends', function() {
        setActiveLink('friends');
    });

    crossroads.addRoute('friendssuggestions', function() {
        setActiveLink('friendssuggestions');
    });

    crossroads.addRoute('tt', function() {
        setActiveLink('tt');
    });

    function parseHash(newHash, oldHash) {
        crossroads.parse(newHash); 
    }
    debugger;
    var config = main.getConfig();
    console.log(config);

    crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
    hasher.initialized.add(parseHash);
    hasher.changed.add(parseHash);
    hasher.init();
});