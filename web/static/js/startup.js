define(['static/js/router.js', 'jquery', 'easing'], function(router, $, easing) {

    //jQuery to collapse the navbar on scroll
    $(window).scroll(function() {
        if ($(".navbar").offset().top > 50) {
            $(".navbar-fixed-top").addClass("top-nav-collapse");
        } else {
            $(".navbar-fixed-top").removeClass("top-nav-collapse");
        }
    });

    //jQuery for page scrolling feature - requires jQuery Easing plugin
    $(function() {
        $('a.page-scroll').bind('click', function(event) {
            var $anchor = $(this);
            $('html, body').stop().animate({
                scrollTop: $($anchor.attr('href')).offset().top - 70
            }, 1500, 'easeInOutExpo');
            event.preventDefault();
        });
    });

    $(document).ready(function () {

        //stick in the fixed 100% height behind the navbar but don't wrap it
        $('#slide-nav.navbar .container').append($('<div id="navbar-height-col"></div>'));
        // Enter your ids or classes
        var toggler = '.navbar-toggle';
        var pagewrapper = '#page-content';
        var navigationwrapper = '.navbar-header';
        var menuwidth = '100%'; // the menu inside the slide menu itself
        var slidewidth = '50%';
        var menuneg = '-100%';
        var slideneg = '-50%';


        $("#slide-nav").on("click", toggler, function (e) {

            var selected = $(this).hasClass('slide-active');

            $('#slidemenu').stop().animate({
                right: selected ? menuneg : '0px'
            });

            $('#navbar-height-col').stop().animate({
                right: selected ? slideneg : '0px'
            });

            $(pagewrapper).stop().animate({
                right: selected ? '0px' : slidewidth
            });

            $(navigationwrapper).stop().animate({
                right: selected ? '0px' : slidewidth
            });


            $(this).toggleClass('slide-active', !selected);
            $('#slidemenu').toggleClass('slide-active');

            $('#page-content, .navbar, body, .navbar-header').toggleClass('slide-active');
        });


        var selected = '#slidemenu, #page-content, body, .navbar, .navbar-header';


        $(window).on("resize", function () {

            if ($(window).width() > 768 && $('.navbar-toggle').is(':hidden')) {
                $(selected).removeClass('slide-active');
            }

        });

    });

});
