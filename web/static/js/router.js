define(['jquery','main',  'crossroads', 'hasher', 'bootstrap'], function(jquery, main, crossroads, hasher) {
'use strict';

    function setActiveLink(hash, param) {

        $.when(main.init()).then(function(){
            main.showSpinner(); //pokaż kręcacz porządnie

            var config = main.getConfig();

            if (main.isUserLoggedIn() == true && main.isUserRegistered() == false){
                require(['lib/pages/register'], function(page) {
                    page.render();
                    main.hideSpinner(); //schowaj kręcacz (?)
                });
            } else if (main.isUserLoggedIn() == false) {
                require(['lib/pages/index'], function(page) {
                    page.render();
                    main.hideSpinner(); //schowaj kręcacz (?)
                });
            } else {

                require(['lib/pages/'+hash], function(page) {
                    page.render();
                    main.hideSpinner(); //schowaj kręcacz (?)
                    $('.navbar li.active').removeClass('active'); //trochę gupio ale na szybko
                    $('.navbar a[href="#'+hash+'"]').parent().addClass('active');
                });
            }
        });
    }

    crossroads.addRoute('', function() {
        setActiveLink('index');
    });

    // "_=_" is added on callback from facebook - should be removed
    crossroads.addRoute('_=_', function() {
        setActiveLink('home');
    });

    crossroads.addRoute('index', function() {
        setActiveLink('index');
    });

    crossroads.addRoute('user', function() {
        setActiveLink('user');
    });

    crossroads.addRoute('user/{id}', function(id) {
        setActiveLink('user',id.id);
    });


    crossroads.addRoute('grades', function() {
        setActiveLink('grades');
    });

    crossroads.addRoute('courses', function() {
        setActiveLink('courses');
    });

    crossroads.addRoute('courses/{id}', function(id) {
        setActiveLink('courses',id.id);
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

    crossroads.addRoute('lecturers/{id}', function(id) {
        setActiveLink('lecturers',id.id);
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

    crossroads.addRoute('home', function() {
        setActiveLink('home');
    });

    function parseHash(newHash, oldHash) {
        crossroads.parse(newHash); 
    }

    crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
    hasher.initialized.add(parseHash);
    hasher.changed.add(parseHash);
    hasher.init();
});