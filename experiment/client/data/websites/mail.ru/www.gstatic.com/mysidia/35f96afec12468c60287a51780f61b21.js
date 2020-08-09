(function(){/*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
'use strict';var aa="function"==typeof Object.create?Object.create:function(a){function b(){}b.prototype=a;return new b},e;if("function"==typeof Object.setPrototypeOf)e=Object.setPrototypeOf;else{var f;a:{var ba={h:!0},h={};try{h.__proto__=ba;f=h.h;break a}catch(a){}f=!1}e=f?function(a,b){a.__proto__=b;if(a.__proto__!==b)throw new TypeError(a+" is not extensible");return a}:null}var k=e;
function l(a,b){a.prototype=aa(b.prototype);a.prototype.constructor=a;if(k)k(a,b);else for(var c in b)if("prototype"!=c)if(Object.defineProperties){var d=Object.getOwnPropertyDescriptor(b,c);d&&Object.defineProperty(a,c,d)}else a[c]=b[c]}var m=this||self,ca=Date.now;function n(a,b){function c(){}c.prototype=b.prototype;a.prototype=new c;a.prototype.constructor=a}function p(a){return a};var da=Array.prototype.forEach?function(a,b){Array.prototype.forEach.call(a,b,void 0)}:function(a,b){for(var c=a.length,d="string"===typeof a?a.split(""):a,g=0;g<c;g++)g in d&&b.call(void 0,d[g],g,a)};var q;function r(a,b){this.b=a===t&&b||"";this.a=u}var u={},t={};function v(a){v[" "](a);return a}v[" "]=function(){};function w(){}var ea="function"==typeof Uint8Array;function x(a,b,c){a.b=null;b||(b=[]);a.j=void 0;a.f=-1;a.a=b;a:{if(b=a.a.length){--b;var d=a.a[b];if(!(null===d||"object"!=typeof d||Array.isArray(d)||ea&&d instanceof Uint8Array)){a.g=b-a.f;a.c=d;break a}}a.g=Number.MAX_VALUE}a.i={};if(c)for(b=0;b<c.length;b++)if(d=c[b],d<a.g)d+=a.f,a.a[d]=a.a[d]||y;else{var g=a.g+a.f;a.a[g]||(a.c=a.a[g]={});a.c[d]=a.c[d]||y}}var y=[];
function z(a,b){if(b<a.g){b+=a.f;var c=a.a[b];return c===y?a.a[b]=[]:c}if(a.c)return c=a.c[b],c===y?a.c[b]=[]:c}function fa(a){a=z(a,2);return null==a?0:a}function ha(a){a=z(a,16);a=null==a?a:!!a;return null==a?!1:a}function A(a,b,c){a.b||(a.b={});if(!a.b[c]){var d=z(a,c);d&&(a.b[c]=new b(d))}return a.b[c]}function B(a){if(a.b)for(var b in a.b){var c=a.b[b];if(Array.isArray(c))for(var d=0;d<c.length;d++)c[d]&&B(c[d]);else c&&B(c)}}w.prototype.toString=function(){B(this);return this.a.toString()};function C(a){x(this,a,ia)}n(C,w);var ia=[17];function D(a){x(this,a,ka)}n(D,w);var ka=[27];function E(a){x(this,a,la)}n(E,w);var la=[8];var F=document;function G(){var a=H;try{var b;if(b=!!a&&null!=a.location.href)a:{try{v(a.foo);b=!0;break a}catch(c){}b=!1}return b}catch(c){return!1}};var I=!!window.google_async_iframe_id,H=I&&window.parent||window,ma,J=new r(t,"//fonts.googleapis.com/css");ma=J instanceof r&&J.constructor===r&&J.a===u?J.b:"type_error:Const";var na;if(void 0===q){var K=null,L=m.trustedTypes;if(L&&L.createPolicy){try{K=L.createPolicy("goog#html",{createHTML:p,createScript:p,createScriptURL:p})}catch(a){m.console&&m.console.error(a.message)}q=K}else q=K}(na=q)&&na.createScriptURL(ma);var M=null;function oa(a,b,c){this.label=a;this.type=b;this.value=c;this.duration=0;this.uniqueId=Math.random();this.slotId=void 0};var N=m.performance,pa=!!(N&&N.mark&&N.measure&&N.clearMarks),O=function(a){var b=!1,c;return function(){b||(c=a(),b=!0);return c}}(function(){var a;if(a=pa){var b;if(null===M){M="";try{a="";try{a=m.top.location.hash}catch(c){a=m.location.hash}a&&(M=(b=a.match(/\bdeid=([\d,]+)/))?b[1]:"")}catch(c){}}b=M;a=!!b.indexOf&&0<=b.indexOf("1337")}return a});
function qa(){var a=P;this.a=[];this.c=a||m;var b=null;a&&(a.google_js_reporting_queue=a.google_js_reporting_queue||[],this.a=a.google_js_reporting_queue,b=a.google_measure_js_timing);this.b=O()||(null!=b?b:1>Math.random())}function ra(a){a&&N&&O()&&(N.clearMarks("goog_"+a.label+"_"+a.uniqueId+"_start"),N.clearMarks("goog_"+a.label+"_"+a.uniqueId+"_end"))}
qa.prototype.start=function(a,b){if(!this.b)return null;var c=void 0===c?m:c;c=c.performance;(c=c&&c.now?c.now():null)||(c=(c=m.performance)&&c.now&&c.timing?Math.floor(c.now()+c.timing.navigationStart):ca());a=new oa(a,b,c);b="goog_"+a.label+"_"+a.uniqueId+"_start";N&&O()&&N.mark(b);return a};if(I&&!G()){var Q="."+F.domain;try{for(;2<Q.split(".").length&&!G();)F.domain=Q=Q.substr(Q.indexOf(".")+1),H=window.parent}catch(a){}G()||(H=window)}var P=H,R=new qa;function sa(){P.google_measure_js_timing||(R.b=!1,R.a!=R.c.google_js_reporting_queue&&(O()&&da(R.a,ra),R.a.length=0))}"number"!==typeof P.google_srt&&(P.google_srt=Math.random());if("complete"==P.document.readyState)sa();else if(R.b){var ta=function(){sa()},ua=P;ua.addEventListener&&ua.addEventListener("load",ta,!1)};function va(){};function S(a,b){a=a.getElementsByTagName("META");for(var c=0;c<a.length;++c)if(a[c].getAttribute("name")===b)return a[c].getAttribute("content");return""};function T(){var a=wa;this.a=a;var b=S(a,"namespace");if(!b){b="ns-"+Math.random().toString(36).substr(2,5);a:{for(var c=a.getElementsByTagName("META"),d=0;d<c.length;++d)if("namespace"===c[d].getAttribute("name")){c[d].setAttribute("content",b);break a}c=a.querySelector("#mys-meta");c||(c=document.createElement("div"),c.id="mys-meta",c.style.position="absolute",c.style.display="none",a.appendChild(c));a=document.createElement("META");a.setAttribute("name","namespace");a.setAttribute("content",b);
c.appendChild(a)}}}T.prototype.dispatchEvent=function(a,b){a=null==b?new CustomEvent(a):new CustomEvent(a,{detail:b});this.a.dispatchEvent(a)};T.prototype.addEventListener=function(a,b){this.a.addEventListener(a,b)};function U(){this.a={}}U.prototype.set=function(a,b){this.a[a]=b};U.prototype.get=function(a){return this.a[a]};function V(a){this.context=a;this.a=new U}l(V,va);function xa(){var a=W;this.b=ya;this.a=a}function za(){var a=Aa,b=Ba;2==fa(b)||A(A(b,D,1),C,10)&&ha(A(A(b,D,1),C,10))||(b=0,mys.engine&&(b=mys.engine.stage()),0==(b&1)&&a.a.addEventListener("overallStart",function(){}),a.a.addEventListener("browserStart",function(){}),a.a.addEventListener("browserReady",function(){}),a.a.addEventListener("browserQuiet",function(){}))};function X(a){V.call(this,a)}l(X,V);function Y(){X.apply(this,arguments)}l(Y,X);function Ca(){Y.apply(this,arguments)}l(Ca,Y);var wa=document.getElementById("mys-content");if(wa){var W=new T,ya=new Ca(W),Aa=new xa,Da=Aa.b.a,Ea=S(W.a,"runtime_data");if(Ea){var Fa=JSON.parse(Ea),Z;for(Z in Fa)Da.set(Z,Fa[Z])}var Ga=S(W.a,"render_config")||"[]",Ba=new E(Ga?JSON.parse(Ga):null);za()};}).call(this);