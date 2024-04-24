odoo.define('website_scorm_elearning.fullscreen_scorm', function (require) {
    'use strict';
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];

    var findSlide = function (slideList, matcher) {
        var slideMatch = _.matcher(matcher);
        return _.find(slideList, slideMatch);
    };

    Fullscreen.include({
        xmlDependencies: (Fullscreen.prototype.xmlDependencies || []).concat(
            ["/website_scorm_elearning/static/src/xml/website_slides_fullscreen.xml"]
        ),
        _preprocessSlideData: function (slidesDataList) {
            var res = this._super.apply(this, arguments);

            slidesDataList.forEach(function (slideData, index) {
                if (slideData.category === 'scorm') {
                    slideData.embedUrl = $(slideData.embedCode).attr('src');
                    slideData.hasQuestion = !!slideData.hasQuestion;
                    try {
                        if (!(slideData.isTimer) && !(slideData.hasQuestion) && !(slideData.is_tincan)) {
                            slideData._autoSetDone = true;
                        }
                    }
                    catch {
                        if (!(slideData.hasQuestion)) {
                            slideData._autoSetDone = true;
                        }
                    }
                }
            });
            return res;
        },

        /**
         * Extend the _renderSlide method so that slides of type "scorm"
         * are also taken into account and rendered correctly
         *
         * @private
         * @override
         */

        _renderSlide: function (){
            var def = this._super.apply(this, arguments);
            var $content = this.$('.o_wslides_fs_content');
            var slideId = this.get('slide');
            if (slideId.category === "scorm"){
                $content.html(QWeb.render('website.slides.fullscreen.content',{widget: this}));
            }
            return Promise.all([def]);
        },

        _onChangeSlide: function () {
            var res = this._super.apply(this, arguments);
            var currentSlide = parseInt(this.$('.o_wslides_fs_sidebar_list_item.active').data('id'));
            var slide = findSlide(this.slides, {id: this.get('slide').id});
            if (!slide.is_tincan && slide.category == 'scorm'){
                this._rpc({
                    route:"/slides/slide/get_scorm_version",
                    params: {
                        'slide_id': currentSlide
                    }
                }).then(function (data){
                    if (slide.completed == undefined) {
                        slide.completed = false;
                    }
                    if (data.scorm_version === 'scorm11') {
                        window.API = new API();
                    }
                    if (data.scorm_version === 'scorm2004') {
                        window.API_1484_11 = new API_1484_11();
                    }
                });
                return res;
            }
        },
    });

    function API(){

        var slideId = parseInt($('.o_wslides_fs_sidebar_list_item.active').data('id'));
        var cur_slide = $('.o_wslides_fs_sidebar_list_item.active');
        try {
            if (!cur_slide.data().isSequential){
                var $slides = $('.o_wslides_fs_sidebar_list_item[data-can-access="True"]');
            }
            else {
                var $slides = $('.o_wslides_fs_sidebar_list_item');
            }
        }
        catch {
            var $slides = $('.o_wslides_fs_sidebar_list_item[data-can-access="True"]');
        }
        var slideList = [];
        $slides.each(function () {
            var slideData = $(this).data();
            slideList.push(slideData);
        });
        var slide = findSlide(slideList, {
            id: slideId,
        });
        this.slide = slide;
        this.values = {};
        rpc.query({
            route: '/slide/slide/get_session_info',
            params: {
                slide_id: this.slide.id,
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
                    slide_id: this.slide.id,
                    element: element,
                    value: value,
                }
            })
            if ((element == 'cmi.completion_status') && (['completed', 'passed'].includes(value))) {
                rpc.query({
                    route: '/slides/slide/set_completed_scorm',
                    params: {
                        slide_id: this.slide.id,
                        completion_type: value,
                }
                }).then(data => {
                    this.slide.completed = true;
                    var $elem = $('.fa-circle-thin[data-slide-id="'+this.slide.id+'"]');
                    $elem.removeClass('fa-circle-thin').addClass('fa-check text-success o_wslides_slide_completed');
                    var channelCompletion = data.channel_completion;
                    var completion = Math.min(100, channelCompletion);
                    $('.progress-bar').css('width', completion + "%" );
                    $('.o_wslides_progress_percentage').text(completion);
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
    function API_1484_11(){

        var slideId = parseInt($('.o_wslides_fs_sidebar_list_item.active').data('id'));
        var cur_slide = $('.o_wslides_fs_sidebar_list_item.active');
        try {
            if (!cur_slide.data().isSequential){
                var $slides = $('.o_wslides_fs_sidebar_list_item[data-can-access="True"]');
            }
            else {
                var $slides = $('.o_wslides_fs_sidebar_list_item');
            }
        }
        catch {
            var $slides = $('.o_wslides_fs_sidebar_list_item[data-can-access="True"]');
        }
        var slideList = [];
        $slides.each(function () {
            var slideData = $(this).data();
            slideList.push(slideData);
        });
        this.slide = findSlide(slideList, {id: slideId});
        this.values = {};
        rpc.query({
            route: '/slide/slide/get_session_info',
            params: {
                slide_id: this.slide.id,
            }
        }).then(data => {
           this.values = data;
        })

        this.Initialize = function(){
            var returnValue = true;
            return returnValue;
        }
        this.SetValue = function(element, value){
            if (isNaN(value)) {
                value = 0;
            }
            this.values[element] = value;
            rpc.query({
                route: '/slide/slide/set_session_info',
                params: {
                    slide_id: this.slide.id,
                    element: element,
                    value: value,
                }
            })
            if (element == 'cmi.core.lesson_status' && (['completed', 'passed'].includes(value))) {
                rpc.query({
                    route: '/slides/slide/set_completed_scorm',
                    params: {
                        slide_id: this.slide.id,
                        completion_type: value,
                }
                }).then(data => {
                    this.slide.completed = true;
                    var $elem = $('.fa-circle-thin[data-slide-id="'+this.slide.id+'"]');
                    $elem.removeClass('fa-circle-thin').addClass('fa-check text-success o_wslides_slide_completed');
                    var channelCompletion = data.channel_completion;
                    var completion = Math.min(100, channelCompletion);
                    $('.progress-bar').css('width', completion + "%" );
                    $('.o_wslides_progress_percentage').text(completion);
                });
            }

            return "true";
        }
        this.GetValue = function(element) {
            var value = this.values[element];
            if (value == undefined) {
                value = '';
            }
            return value;
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
});