define(['jquery',  'bootstrap', 'router', 'datatables'],
function($, bootstrap, router, datatables) {

//        //jQuery to collapse the navbar on scroll
//        $(window).scroll(function() {
//            if ($(".navbar").offset().top > 50) {
//                $(".navbar-fixed-top").addClass("top-nav-collapse");
//            } else {
//                $(".navbar-fixed-top").removeClass("top-nav-collapse");
//            }
//        });
//
//        var kolumnaPrawa =  $("div.border-logo-cykle").height();
//        var kolumnaLewa = $("div.border-logo-cykle").height();
//
//        if (kolumnaLewa > kolumnaPrawa)
//        {
//            $("div.border-logo-cykle").css({'height' : kolumnaLewa});
//        }
//        else
//        {
//            $("div.border-logo-cykle").css({'height' : kolumnaPrawa});
//        };
//
//        //stick in the fixed 100% height behind the navbar but don't wrap it
//        $('#slide-nav.navbar .container-fluid').append($('<div id="navbar-height-col"></div>'));
//        $('#slide-nav.navbar .container').append($('<div id="navbar-height-col"></div>'));
//        // Enter your ids or classes
//        var toggler = '.navbar-toggle';
//        var pagewrapper = '#page-content';
//        var navigationwrapper = '.navbar-header';
//        var menuwidth = '100%'; // the menu inside the slide menu itself
//        var slidewidth = '50%';
//        var menuneg = '-100%';
//        var slideneg = '-50%';
//
//
//        $("#slide-nav").on("click", toggler, function (e) {
//
//            var selected = $(this).hasClass('slide-active');
//
//            $('#slidemenu').stop().animate({
//                right: selected ? menuneg : '0px'
//            });
//
//            $('#navbar-height-col').stop().animate({
//                right: selected ? slideneg : '0px'
//            });
//
//            $(pagewrapper).stop().animate({
//                right: selected ? '0px' : slidewidth
//            });
//
//            $(navigationwrapper).stop().animate({
//                right: selected ? '0px' : slidewidth
//            });
//
//
//            $(this).toggleClass('slide-active', !selected);
//            $('#slidemenu').toggleClass('slide-active');
//
//
//            $('#page-content, .navbar, body, .navbar-header').toggleClass('slide-active');
//
//        });
//
//
//        $(window).scroll(function() {
//            if ($(".navbar").offset().top > 50) {
//                $(".navbar-fixed-top").addClass("top-nav-collapse");
//            } else {
//                $(".navbar-fixed-top").removeClass("top-nav-collapse");
//            }
//        });

});
