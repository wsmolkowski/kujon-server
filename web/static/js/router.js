define(['jquery', 'main', 'handlebars',  'crossroads', 'hasher', 'bootstrap', 'text!templates/spinner.html',], function(
jquery, main, Handlebars, crossroads, hasher, bootstrap, spinnerTpl) {
'use strict';

    var template = Handlebars.compile(spinnerTpl);

    function setActiveLink(hash) {

        $('#page-content').html(template());

        require(['lib/pages/'+hash], function(page) {
            page.render();

            $('.navbar li.active').removeClass('active'); //trochę gupio ale na szybko
            $('.navbar a[href="#'+hash+'"]').parent().addClass('active');

            //schowaj kręcacz (?)
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

    crossroads.addRoute('faculties', function() {
        setActiveLink('faculties');
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

    crossroads.addRoute('friends', function() {
        setActiveLink('friends');
    });

    crossroads.addRoute('friendssuggestions', function() {
        setActiveLink('friendssuggestions');
    });

    crossroads.addRoute('tt', function() {
        setActiveLink('tt');
    });

    crossroads.addRoute('contact', function() {
        setActiveLink('contact');
    });

    crossroads.addRoute('404', function() {
        setActiveLink('404');
    });

    function parseHash(newHash, oldHash) {
        crossroads.parse(newHash); 
    }

    crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
    hasher.initialized.add(parseHash);
    hasher.changed.add(parseHash);
    hasher.init();
});