"use strict";(self["webpackChunk_jupyterlab_application_top"]=self["webpackChunk_jupyterlab_application_top"]||[]).push([[9109],{39109:(e,t,r)=>{r.r(t);r.d(t,{webIDL:()=>_});function a(e){return new RegExp("^(("+e.join(")|(")+"))\\b")}var n=["Clamp","Constructor","EnforceRange","Exposed","ImplicitThis","Global","PrimaryGlobal","LegacyArrayClass","LegacyUnenumerableNamedProperties","LenientThis","NamedConstructor","NewObject","NoInterfaceObject","OverrideBuiltins","PutForwards","Replaceable","SameObject","TreatNonObjectAsNull","TreatNullAs","EmptyString","Unforgeable","Unscopeable"];var i=a(n);var l=["unsigned","short","long","unrestricted","float","double","boolean","byte","octet","Promise","ArrayBuffer","DataView","Int8Array","Int16Array","Int32Array","Uint8Array","Uint16Array","Uint32Array","Uint8ClampedArray","Float32Array","Float64Array","ByteString","DOMString","USVString","sequence","object","RegExp","Error","DOMException","FrozenArray","any","void"];var c=a(l);var o=["attribute","callback","const","deleter","dictionary","enum","getter","implements","inherit","interface","iterable","legacycaller","maplike","partial","required","serializer","setlike","setter","static","stringifier","typedef","optional","readonly","or"];var f=a(o);var s=["true","false","Infinity","NaN","null"];var m=a(s);var u=["callback","dictionary","enum","interface"];var p=a(u);var y=["typedef"];var b=a(y);var d=/^[:<=>?]/;var v=/^-?([1-9][0-9]*|0[Xx][0-9A-Fa-f]+|0[0-7]*)/;var h=/^-?(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+)/;var A=/^_?[A-Za-z][0-9A-Z_a-z-]*/;var g=/^_?[A-Za-z][0-9A-Z_a-z-]*(?=\s*;)/;var k=/^"[^"]*"/;var D=/^\/\*.*?\*\//;var C=/^\/\*.*/;var E=/^.*?\*\//;function w(e,t){if(e.eatSpace())return null;if(t.inComment){if(e.match(E)){t.inComment=false;return"comment"}e.skipToEnd();return"comment"}if(e.match("//")){e.skipToEnd();return"comment"}if(e.match(D))return"comment";if(e.match(C)){t.inComment=true;return"comment"}if(e.match(/^-?[0-9\.]/,false)){if(e.match(v)||e.match(h))return"number"}if(e.match(k))return"string";if(t.startDef&&e.match(A))return"def";if(t.endDef&&e.match(g)){t.endDef=false;return"def"}if(e.match(f))return"keyword";if(e.match(c)){var r=t.lastToken;var a=(e.match(/^\s*(.+?)\b/,false)||[])[1];if(r===":"||r==="implements"||a==="implements"||a==="="){return"builtin"}else{return"type"}}if(e.match(i))return"builtin";if(e.match(m))return"atom";if(e.match(A))return"variable";if(e.match(d))return"operator";e.next();return null}const _={name:"webidl",startState:function(){return{inComment:false,lastToken:"",startDef:false,endDef:false}},token:function(e,t){var r=w(e,t);if(r){var a=e.current();t.lastToken=a;if(r==="keyword"){t.startDef=p.test(a);t.endDef=t.endDef||b.test(a)}else{t.startDef=false}}return r},languageData:{autocomplete:n.concat(l).concat(o).concat(s)}}}}]);