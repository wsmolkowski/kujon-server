define(['jquery','crossroads', 'hasher', 'bootstrap'], function(jquery, crossroads, hasher) {
'use strict';
    
    function setActiveLink(hash) {  
        //console.log(hash);
        
        //pokaż kręcacz porządnie
        $('#page').html('Loading...');
        
        require(['static/js/pages/'+hash], function(page) {
            page.render();  
            
            $('.navbar li.active').removeClass('active'); //trochę gupio ale na szybko
            $('.navbar a[href="#'+hash+'"]').parent().addClass('active');
            
            //schowaj kręcacz (?)            
        });
    }
    
    crossroads.addRoute('', function() {
        setActiveLink('home');
    });
    
    crossroads.addRoute('home', function() {
        setActiveLink('home');
    });
    
    crossroads.addRoute('user', function() {
        setActiveLink('user');
    });
    
    crossroads.addRoute('about', function() {
        setActiveLink('about');
    });
    
    function parseHash(newHash, oldHash) { 
        crossroads.parse(newHash); 
    }
    
    crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
    hasher.initialized.add(parseHash);
    hasher.changed.add(parseHash);
    hasher.init();
});