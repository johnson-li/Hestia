(function(){document.getElementById("suggest-container")||$("#search-block .search-suggest").prepend('<div id="suggest-container" style="display:none" class="suggest"><div class="suggest-bd"></div><div class="suggest-ft"></div></div>');var e=qboot.jsonp,t="suggest-container",n="haosou-input",r="search-block",i="search-hotword";if(!$("#"+n)[0])return;var s=$("#"+n)[0],o=$("#"+r)[0],u=$("#"+t)[0],a=$("#"+t+" .suggest-bd")[0],f=s.form,l=new qSuggest(s,{autoPosition:!1,uiReferElem:o,uiWrapElem:u,uiContainerElem:a,posAdjust:{width:-2,top:-1},recAllTimeout:120});(function(){function b(){u.hide(),$(o).removeClass("search-block-active")}function w(){u.show(),$(o).addClass("search-block-active")}function E(){u.render(),$(o).addClass("search-block-active")}var r=qSuggest.log,s=l,u=s.ui,a=s.data,f="reci",c="direct",h="common",p="on",d={},v={},m=function(e){return String(e).replace(/[^\x00-\xff]/g,"abc").replace(/[\d]/g,"abc").length},g="",y=!1;d[h]=[1,50],d[c]=[6,50],v[h]=[],v[c]=[],v[f]=[],u.searchForm.on("submit",function(e){var t=u.getFocusedGroup();if(t==c){var n=$("#suggest-direct>a."+p);n[0]&&y&&(window.open(n.attr("href")),e.preventDefault&&e.preventDefault(),y=!1)}else{var n=$("#suggest-reci>a."+p);t==f&&n[0]&&n.attr("href")&&y&&(window.open(n.attr("href")),e.preventDefault&&e.preventDefault(),y=!1)}u.getTextInputVal()==s.query,g=u.getTextInputVal()}),$(".btn-submit").on("click",function(){u.searchForm.trigger("submit")}),function(){var e=null,t=window.hotwordData=[],n=[],r={},o="g-arrow-up",a="//mbsug.ssl.so.com/sug-hot";$.ajax({url:a,data:{channel:"type_news",realhot_limit:10,src:"home_hot",callback:"jsonp"},type:"get",dataType:"jsonp",success:function(e){e.errno==0&&e.data&&e.data.length>0&&(n=e.data,t=window.hotwordData=n)},dataType:"jsonp",jsonpCallback:"hotword"}),u.on("change",function(e){e.query||b()}),u.textInput.on("mousedown",function(e){u.getTextInputVal().trim()==""&&($("#suggest-reci")[0]?$("#suggest-container").is(":visible")?b():w():(s.query="",E()),u.focusTextInput(),u.on("change",function(e){b(),u.off("change",arguments.callee)}))}),u.textInput.on("keydown",function(e){var t=u.container.html()?!0:!1;!t&&e.keyCode==40&&u.getTextInputVal().trim()==""&&$("#"+i).trigger("click")}),u.bindGroupHandler(f,{render:{setup:function(){v[f]=[]},build:function(){if(s.query==""){if(t&&t.length>0){if(!e){e={};var n="",r=e.total=t.length,a="",l=[];for(var c=0;c<r;c++)c===0?a="<em class='first'>"+(c+1)+"</em>":c===1?a="<em class='second'>"+(c+1)+"</em>":c===2?a="<em class='third'>"+(c+1)+"</em>":a="<em>"+(c+1)+"</em>",l=[],+t[c].is_new&&l.push("new"),n+="<a"+(t[c].url?' href="'+t[c].url+'"':"")+' data-text="'+t[c].title+'" data-index="'+c+'">'+a+'<span class="'+l.join(" ")+'">'+t[c].title+"</span></a>";e.content=n?'<div id="suggest-reci">'+n+'<div class="reci-setting"></div></div>':""}return u.setGroupTotal(f,e.total),e.content}return""}$("#"+i).removeClass(o)},teardown:function(){v[f]=$("#suggest-reci>a")}},init:function(){u.initGroupUserBehavior(f,"#suggest-reci>a"),u.container.delegate("#suggest-reci>a","click",function(e){$(this).attr("href")||e.preventDefault()}),u.on("itemSelect",function(e){if(e.group!==f)return;if(e.index>-1&&v[f][e.index]){var t=v[f].eq(e.index),n=t.attr("data-text");e.trigger!="keyboard"&&u.setTextInputVal(n),t.attr("href")?e.trigger=="keyboard"&&u.getTextInputVal()==n&&(y=!0):u.trigger("enter",{trigger:e.trigger}),t.attr("href")}}),u.on("itemFocus",function(e){if(e.group!==f)return;if(e.index>-1&&v[f][e.index]){var t=v[f].eq(e.index);t.addClass(p),e.trigger==="keyboard"&&u.setTextInputVal(t.attr("data-text"))}}),u.on("itemBlur",function(e){if(e.group!==f)return;e.index>-1&&v[f][e.index]&&v[f].eq(e.index).removeClass(p)})}})}(),function(){a.bindGroupHandler(c,{request:function(e,t){if(!t||!e)return;return;var n},receive:function(e){return e&&e.errno===0?{query:e.kw,data:e}:null}}),u.bindGroupHandler(c,{render:{setup:function(){v[c]=[]},build:function(e){if(!e)return"";var t="",n=e.app,r=e.res[0];n==="video"&&(t='<a class="video" data-subApp="'+n+'" data-text="'+r[0]+'" data-index="0" href="'+r[2]+'" hidefocus="false" style="outline:0;" target="_blank"><h2><strong>'+r[0]+"</strong> "+r[1]+'<ins class="hdicon"></ins></h2><div class="meta">'+r[3]+'</div><div class="meta">'+r[4]+"</div></a>"),n==="website"&&(t='<a class="website" data-subApp="'+n+'" data-text="'+r[0]+'" data-index="0" href="'+r[2]+'" hidefocus="false" style="outline:0;" target="_blank"><h2><img src="'+r[4]+'" /><strong>'+r[0]+"</strong> - "+r[3]+'</h2><div class="meta">'+r[1]+"</div></a>");if(n==="caipiao"||n==="mall"||n==="tuan"||n==="game")t='<a class="'+n+'" data-subApp="'+n+'" data-text="'+r[0]+'" data-index="0" href="'+r[2]+'" hidefocus="false" style="outline:0;" target="_blank"><h2><strong>'+r[0]+"</strong> - "+r[1]+'</h2><div class="meta">'+r[3]+"</div></a>";return t=t?'<div id="suggest-direct">'+t+"</div>":"",t&&u.setGroupTotal(c,1),t},teardown:function(){v[c]=$("#suggest-direct>a")}},init:function(){u.initGroupUserBehavior(c,"#suggest-direct>a"),u.on("itemSelect",function(e){if(e.group===c){r("itemSelect[DIRECT] index:"+e.index);if(e.index>-1&&v[c][e.index]){var t=v[c].eq(e.index),n=t.attr("data-text");e.trigger=="keyboard"&&u.getTextInputVal()==n?y=!0:e.trigger!="keyboard"&&u.setTextInputVal(n)}}}),u.on("itemFocus",function(e){if(e.group!==c)return;if(e.index>-1&&v[c][e.index]){var t=v[c].eq(e.index);t.addClass(p),e.trigger==="keyboard"&&u.setTextInputVal(t.attr("data-text"))}}),u.on("itemBlur",function(e){if(e.group!==c)return;e.index>-1&&v[c][e.index]&&v[c].eq(e.index).removeClass(p)})}})}(),function(){a.bindGroupHandler(h,{request:function(t,n){if(!n||!t)return;var r=m(t);r>=d[h][0]&&r<=d[h][1]&&e("//sug.so.360.cn/suggest?word="+encodeURIComponent(t)+"&encodein=utf-8&encodeout=utf-8&pq="+encodeURIComponent(g),function(e,t){n(e)},{jsonp:"callback"})},receive:function(e){return e&&e.q&&e.s&&e.s.length>0?{query:e.q,data:e.s}:null}}),u.bindGroupHandler(h,{render:{setup:function(){v[h]=[]},build:function(){var e=0;return function(t){if(!t)return"";var n="",r,i=s.query.length,a=0;u.setGroupTotal(h,t.length);for(var f=0,l=t.length;f<l;f++){t[f]=t[f].trim(),r=t[f].toLowerCase();if(r===s.query)continue;r.indexOf(s.query)===0&&(r=s.query+"<b>"+r.substring(i)+"</b>"),n+='<a data-text="'+t[f]+'" data-index="'+a+'"  class="suggest-item">'+r+"</a>",a++}return n=n?'<div id="suggest-common" class="suggest-list">'+n+"</div>":"",$(o).addClass("search-block-active"),e!=l&&(e=l,$(".suggest-ft .declare").css("position","relative").css("position","absolute")),n}}(),teardown:function(){v[h]=$("#suggest-common>a")}},init:function(){u.initGroupUserBehavior(h,"#suggest-common>a"),u.container.delegate("#suggest-common>a","click",function(e){e.preventDefault()}),u.on("itemSelect",function(e){if(e.group!==h)return;if(e.index>-1&&v[h][e.index]){var t=v[h].eq(e.index);e.trigger!="keyboard"&&u.setTextInputVal(t.attr("data-text")),u.trigger("enter",{trigger:e.trigger}),r("itemSelect[COMMON] index:"+e.index),s.renderQuery!=s.query}}),u.on("itemFocus",function(e){if(e.group!==h)return;if(e.index>-1&&v[h][e.index]){var t=v[h].eq(e.index);t.addClass(p),e.trigger=="keyboard"&&u.setTextInputVal(t.attr("data-text"))}}),u.on("itemBlur",function(e){if(e.group!==h)return;e.index>-1&&v[h][e.index]&&v[h].eq(e.index).removeClass(p)})}})}(),u.on("itemSelect",function(e){setTimeout(function(){b()},300)}),$(document).on("mouseup",function(e){var r=$(e.target);(!r.attr("id")||[n,t,i].indexOf(r.attr("id"))==-1)&&!r.parents("#"+n)[0]&&!r.parents("#"+t)[0]&&!r.parents("#"+i)[0]&&(b(),$(".search-tabs-list").hide())}),$(window).on("blur",function(){b(),$(".search-tabs-list").hide()}),$(".search-tabs").on("click",function(e){e.preventDefault(),$(o).addClass("search-block-active"),$(".search-tabs-list").show()}),$(".search-tabs-list a").on("click",function(e){e.preventDefault();var t=$("#search-form"),n=$(".search-tabs"),r=$(this).text(),i=$(this).attr("href");t.attr("action",i),n.text(r),$(o).removeClass("search-block-active"),$(this).siblings().removeClass("cur"),$(this).addClass("cur"),$(".search-tabs-list").hide()})})()})();