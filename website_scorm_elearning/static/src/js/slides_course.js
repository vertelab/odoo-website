odoo.define('website_scorm_elearning.scorm', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    var publicWidget = require('web.public.widget');

    function API(slide, slide_type){

        this.values = {};
        rpc.query({
            route: '/slide/slide/get_session_info',
            params: {
                slide_id: slide
            }
        }).then(data => {
           this.values = data;
        })

        this.LMSInitialize = function(){
            return "true";
        }
        this.LMSSetValue = function(element, value){
            this.values[element] = value;
            rpc.query({
                route: '/slide/slide/set_session_info',
                params: {
                    slide_id: slide,
                    element: element,
                    value: value,
                }
            })
            if ((element == 'cmi.completion_status') && (['completed', 'passed'].includes(value))) {
                rpc.query({
                    route: '/slides/slide/set_completed_scorm',
                    params: {
                        slide_id: slide,
                        completion_type: value,
                }
                }).then(data => {
                    var $elem = $('#o_wslides_lesson_aside_slide_check_'+ slide);
                    $elem.removeClass('fa-circle text-600').addClass('text-success fa-check-circle');
                    var channelCompletion = data.channel_completion;
                    var completion = Math.min(100, channelCompletion);
                    $('.progress-bar').css('width', completion + "%" );
                    $('.text-white-50').text(completion + " %");
                });
            };
            return "true";
        }
        this.LMSGetValue = function(element) {
            return this.values[element];
        }
        this.LMSGetLastError = function() {
            return 0;
        }
        this.LMSGetErrorString = function(errorCode) {
            return "error string";
        }
        this.LMSGetDiagnostic = function(errorCode) {
            return "diagnostic string";
        }
        this.LMSCommit = function() {
            this.LMSGetValue('');
            return "true";
        }
        this.LMSFinish = function() {
            return "true";
        }
    }
    function API_1484_11(currentSlide, slide_type){

        this.values = {};
        rpc.query({
            route: '/slide/slide/get_session_info',
            params: {
                slide_id: currentSlide,
            }
        }).then(data => {
           this.values = data;
        })

        this.Initialize = function(){
            var returnValue = true;
            return returnValue;
        }
        this.SetValue = function(element, value){
            this.values[element] = value;
            rpc.query({
                route: '/slide/slide/set_session_info',
                params: {
                    slide_id: currentSlide,
                    element: element,
                    value: value,
                }
            })
            if (element == 'cmi.core.lesson_status' && (['completed', 'passed'].includes(value))) {
                rpc.query({
                    route: '/slides/slide/set_completed_scorm',
                    params: {
                        slide_id: currentSlide,
                        completion_type: value,
                    }
                }).then(data => {
                    var $elem = $('#o_wslides_lesson_aside_slide_check_'+ currentSlide);
                    $elem.removeClass('fa-circle text-600').addClass('text-success fa-check-circle');
                    var channelCompletion = data.channel_completion;
                    var completion = Math.min(100, channelCompletion);
                    $('.progress-bar').css('width', completion + "%" );
                    $('.text-white-50').text(completion + " %");
                });
            }

            return "true";
        }
        this.GetValue = function(element) {
            return this.values[element];
        }
        this.GetLastError = function() {
            return 0;
        }
        this.GetErrorString = function(errorCode) {
            return "error string";
        }
        this.GetDiagnostic = function(errorCode) {
            return "diagnostic string";
        }
        this.Commit = function() {
            return true;
        }
        this.Terminate = function() {
            return "true";
        }
    }

    publicWidget.registry.Scorm = publicWidget.Widget.extend({
        selector: '.o_wslides_lesson_content_type',

        /**
         * @override
         */
        start: function () {
            var currentSlide = parseInt($('#scorm_content').attr('slide_id'));
            $('#scorm_content').append($('#iframe_src').attr('value'));
            $('#iframe_src').remove();
            if (!(isNaN(currentSlide))) {
                this._rpc({
                    route:"/slides/slide/get_scorm_version",
                    params: {
                        'slide_id': currentSlide
                    }
                }).then(function (data){
                    if (data.scorm_version === 'scorm11') {
                        window.API = new API(currentSlide, 'scorm');
                    }
                    if (data.scorm_version === 'scorm2004') {
                        window.API_1484_11 = new API_1484_11(currentSlide, 'scorm');
                    }
                });
            }
        },
    });
});