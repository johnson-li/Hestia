/* virtuals-investment/1.0 index.js Date:2017-01-06 17:53:46 */
~function(){var a={temp:function(a,b){var c="var p=[],print=function(){p.push.apply(p,arguments);};with(obj){p.push('"+a.replace(/[\r\t\n]/g," ").split("<%").join("	").replace(/((^|%>)[^\t]*)'/g,"$1\r").replace(/\t=(.*?)%>/g,"',$1,'").split("	").join("');").split("%>").join("p.push('").split("\r").join("\\'")+"');}return p.join('');";return fn=new Function("obj",c),b?fn(b):fn},getAjax:function(a,b,c,d){$.ajax({type:a||"post",url:"//corporate.jd.com"+b,dataType:c||"json",success:function(a){1==a.code&&a.data.length&&d&&d(a.data)},error:function(){}})}};var b={slider:'<div class="item <%=status%>"><a href="<%=contentRedirectUrl%>" target="_blank"><img src="<%=contentTopicImgUrl%>"><div class="slide-caption"><h3><%=contentTopic%></h3><p><%=contentSummary%></p></div></a></div>',new1:'<a class="col-md-4 col-sm-12 col-xs-12 mc-fore" href="<%=contentRedirectUrl%>"><div class="fore fore1"><h4><%=contentTopic%></h4><p><%=contentSummary%></p><i class="fa-triangle"></i></div></a>',control:'<li data-target="#carouse" data-slide-to="<%=index%>" class="<%=status%>"></li>'};var c=function(){a.getAjax("post","/home/sliderPicList","json",function(c){var d=$("#carouse");var e="";var f="";$.each(c,function(c,d){d.status=0==c?"active":"",d.index=c,e+=a.temp(b.slider,d),f+=a.temp(b.control,d)}),d.find(".carousel-inner").html(e),d.find(".carousel-indicators").html(f),d.removeClass("carouse-loading"),d.carousel({interval:5e3,pause:"hover",wrap:!0,keyboard:!0})}),a.getAjax("post","/home/newsAnnouncementsList","json",function(c){var d=$(".news-mc");var e="";$.each(c,function(c,d){e+=a.temp(b.new1,d)}),d.html(e)})};c()}();