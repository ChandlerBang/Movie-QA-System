/*
 * poposliders - v1.0.0 - 2015-06-10
 * http://po-po.github.io/
 *
 * Copyright (c) 2015 popo;
 * Licensed under the MIT license
 */
(function($) {
    $.fn.poposlides = function(options) {

        var settings = $.extend({
            auto:true,             //自动播放
            nav:true,              //切换按钮
            playspeed:3500,         //自动播放速度
            fadespeed:500,         //淡入淡出速度
            loop:true,             //循环播放
            pagination:true,       //页码显示
			pagecenter:true,       //页码居中
            prev:".prev",          //上一页按钮
            next:".next"           //下一页按钮
            }, options);

        return this.each(function() {

            var $this = $(this),
                slide = $this.children(),
                index = 0;
                len = slide.length-1,
                slideWidth = $this.width(),
                prev = settings.prev,
                next = settings.next;

            //初始隐藏其它页，显示当前页
			if(!navigator.userAgent.match(/mobile/i)){
				slide.fadeOut(settings.fadespeed).css({
					"z-index":"0"
				});
				slide.eq(index).fadeIn(settings.fadespeed).css({
					"z-index":"9"
				});
			}else{
				slide.css({
					"opacity":"0",
					"z-index":"0"
				});
				slide.eq(index).css({
					"opacity":"1",
					"z-index":"9"
				});
			};
            //显示当前页
            slideFadeIn = function(){
				if(!navigator.userAgent.match(/mobile/i)){
					slide.fadeOut(settings.fadespeed).css({
						"z-index":"0"
					});
					slide.eq(index).fadeIn(settings.fadespeed).css({
						"z-index":"9"
					});
				}else{
					slide.css({
						"opacity":"0",
						"z-index":"0",
						"-webkit-transition": settings.fadespeed/1000+"s"
					});
					slide.eq(index).css({
						"opacity":"1",
						"z-index":"9",
						"-webkit-transition": settings.fadespeed/1000+"s"
					});
				};
            };

            //翻页加，判断是否循环
            slideAdd = function() {
            	if(settings.loop){
					index == len?index=0:index++;
				}else{
					index == len?index=len:index++;
				};
        		slideFadeIn();
            };

            //翻页减，判断是否循环
            slideMinus = function() {
            	if(settings.loop){
					index == 0?index=len:index--;
				}else{
					index == 0?index=0:index--;
				};
        		slideFadeIn();
            };

            //页码
            pagnation = function(){
            	var $paginationBox = $("<ul class='pagination'></ul>");
            	var paginationStr ="";
				for(var i=1;i<=len+1;i++){
					paginationStr +="<li><a href='javascript:void(0)'>"+ i +"</a>";
				}
				$paginationBox.append(paginationStr);
				$this.after($paginationBox);

				$(".pagination li a").eq(index).addClass("active");

            };

            //当前页码
            pageActive = function(){
				$(".pagination li a").removeAttr("class")
            	$(".pagination li a").eq(index).addClass("active");
			}

			//是否需要左右导航图标
            if(settings.nav) {
				var navStr = "<a href='javascript:void(0)' class="+ prev.substring(1) +"></a>" +
							 "<a href='javascript:void(0)' class="+ next.substring(1) +"></a>";
				$this.after(navStr);

                $(next).click(function(){
                	slideAdd();
                });

                $(prev).click(function(){
                	slideMinus();
                })
			};

			//是否需要页码
			if(settings.pagination) {
				pagnation();
				$(prev).click(function(){ pageActive();});
				$(next).click(function(){ pageActive();});

                $(".pagination li").click(function(){
                	var idx = $(this).index()-1;
                	index = idx;
                	slideAdd();
                	pageActive();
                });
			};

			//页码居中
			if(settings.pagecenter){
				var pw = $(".pagination").width();
				$(".pagination").css({
					"position":"absolute",
					"left":"50%",
					"bottom":"5px",
					"margin-left":-pw/2,
					"z-index": "99"
				})
			};

			//是否自动播放
			if(settings.auto){
		        var play = setInterval(function(){
		        	slideAdd();
		        	pageActive();
		        },settings.playspeed);
		        $this.nextAll().hover(function () {
		            clearInterval(play);
		        },
		        function(){
		        	play = setInterval(function(){
		        		slideAdd();
		        		pageActive();
		        	},settings.playspeed);
		        });
            };

        });
    };

})(jQuery);