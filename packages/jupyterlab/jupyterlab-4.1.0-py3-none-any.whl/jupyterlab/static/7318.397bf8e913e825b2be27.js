"use strict";(self["webpackChunk_jupyterlab_application_top"]=self["webpackChunk_jupyterlab_application_top"]||[]).push([[7318],{27318:(e,r,t)=>{t.r(r);t.d(r,{javascript:()=>i,json:()=>a,jsonld:()=>u,typescript:()=>f});function n(e){var r=e.statementIndent;var t=e.jsonld;var n=e.json||t;var i=e.typescript;var a=e.wordCharacters||/[\w$\xa1-\uffff]/;var u=function(){function e(e){return{type:e,style:"keyword"}}var r=e("keyword a"),t=e("keyword b"),n=e("keyword c"),i=e("keyword d");var a=e("operator"),u={type:"atom",style:"atom"};return{if:e("if"),while:r,with:r,else:t,do:t,try:t,finally:t,return:i,break:i,continue:i,new:e("new"),delete:n,void:n,throw:n,debugger:e("debugger"),var:e("var"),const:e("var"),let:e("var"),function:e("function"),catch:e("catch"),for:e("for"),switch:e("switch"),case:e("case"),default:e("default"),in:a,typeof:a,instanceof:a,true:u,false:u,null:u,undefined:u,NaN:u,Infinity:u,this:e("this"),class:e("class"),super:e("atom"),yield:n,export:e("export"),import:e("import"),extends:n,await:n}}();var f=/[+\-*&%=<>!?|~^@]/;var s=/^@(context|id|value|language|type|container|list|set|reverse|index|base|vocab|graph)"/;function o(e){var r=false,t,n=false;while((t=e.next())!=null){if(!r){if(t=="/"&&!n)return;if(t=="[")n=true;else if(n&&t=="]")n=false}r=!r&&t=="\\"}}var l,c;function d(e,r,t){l=e;c=t;return r}function m(e,r){var t=e.next();if(t=='"'||t=="'"){r.tokenize=p(t);return r.tokenize(e,r)}else if(t=="."&&e.match(/^\d[\d_]*(?:[eE][+\-]?[\d_]+)?/)){return d("number","number")}else if(t=="."&&e.match("..")){return d("spread","meta")}else if(/[\[\]{}\(\),;\:\.]/.test(t)){return d(t)}else if(t=="="&&e.eat(">")){return d("=>","operator")}else if(t=="0"&&e.match(/^(?:x[\dA-Fa-f_]+|o[0-7_]+|b[01_]+)n?/)){return d("number","number")}else if(/\d/.test(t)){e.match(/^[\d_]*(?:n|(?:\.[\d_]*)?(?:[eE][+\-]?[\d_]+)?)?/);return d("number","number")}else if(t=="/"){if(e.eat("*")){r.tokenize=k;return k(e,r)}else if(e.eat("/")){e.skipToEnd();return d("comment","comment")}else if(er(e,r,1)){o(e);e.match(/^\b(([gimyus])(?![gimyus]*\2))+\b/);return d("regexp","string.special")}else{e.eat("=");return d("operator","operator",e.current())}}else if(t=="`"){r.tokenize=v;return v(e,r)}else if(t=="#"&&e.peek()=="!"){e.skipToEnd();return d("meta","meta")}else if(t=="#"&&e.eatWhile(a)){return d("variable","property")}else if(t=="<"&&e.match("!--")||t=="-"&&e.match("->")&&!/\S/.test(e.string.slice(0,e.start))){e.skipToEnd();return d("comment","comment")}else if(f.test(t)){if(t!=">"||!r.lexical||r.lexical.type!=">"){if(e.eat("=")){if(t=="!"||t=="=")e.eat("=")}else if(/[<>*+\-|&?]/.test(t)){e.eat(t);if(t==">")e.eat(t)}}if(t=="?"&&e.eat("."))return d(".");return d("operator","operator",e.current())}else if(a.test(t)){e.eatWhile(a);var n=e.current();if(r.lastType!="."){if(u.propertyIsEnumerable(n)){var i=u[n];return d(i.type,i.style,n)}if(n=="async"&&e.match(/^(\s|\/\*([^*]|\*(?!\/))*?\*\/)*[\[\(\w]/,false))return d("async","keyword",n)}return d("variable","variable",n)}}function p(e){return function(r,n){var i=false,a;if(t&&r.peek()=="@"&&r.match(s)){n.tokenize=m;return d("jsonld-keyword","meta")}while((a=r.next())!=null){if(a==e&&!i)break;i=!i&&a=="\\"}if(!i)n.tokenize=m;return d("string","string")}}function k(e,r){var t=false,n;while(n=e.next()){if(n=="/"&&t){r.tokenize=m;break}t=n=="*"}return d("comment","comment")}function v(e,r){var t=false,n;while((n=e.next())!=null){if(!t&&(n=="`"||n=="$"&&e.eat("{"))){r.tokenize=m;break}t=!t&&n=="\\"}return d("quasi","string.special",e.current())}var y="([{}])";function w(e,r){if(r.fatArrowAt)r.fatArrowAt=null;var t=e.string.indexOf("=>",e.start);if(t<0)return;if(i){var n=/:\s*(?:\w+(?:<[^>]*>|\[\])?|\{[^}]*\})\s*$/.exec(e.string.slice(e.start,t));if(n)t=n.index}var u=0,f=false;for(var s=t-1;s>=0;--s){var o=e.string.charAt(s);var l=y.indexOf(o);if(l>=0&&l<3){if(!u){++s;break}if(--u==0){if(o=="(")f=true;break}}else if(l>=3&&l<6){++u}else if(a.test(o)){f=true}else if(/["'\/`]/.test(o)){for(;;--s){if(s==0)return;var c=e.string.charAt(s-1);if(c==o&&e.string.charAt(s-2)!="\\"){s--;break}}}else if(f&&!u){++s;break}}if(f&&!u)r.fatArrowAt=s}var b={atom:true,number:true,variable:true,string:true,regexp:true,this:true,import:true,"jsonld-keyword":true};function h(e,r,t,n,i,a){this.indented=e;this.column=r;this.type=t;this.prev=i;this.info=a;if(n!=null)this.align=n}function x(e,r){for(var t=e.localVars;t;t=t.next)if(t.name==r)return true;for(var n=e.context;n;n=n.prev){for(var t=n.vars;t;t=t.next)if(t.name==r)return true}}function g(e,r,t,i,a){var u=e.cc;V.state=e;V.stream=a;V.marked=null;V.cc=u;V.style=r;if(!e.lexical.hasOwnProperty("align"))e.lexical.align=true;while(true){var f=u.length?u.pop():n?F:B;if(f(t,i)){while(u.length&&u[u.length-1].lex)u.pop()();if(V.marked)return V.marked;if(t=="variable"&&x(e,i))return"variableName.local";return r}}}var V={state:null,column:null,marked:null,cc:null};function A(){for(var e=arguments.length-1;e>=0;e--)V.cc.push(arguments[e])}function z(){A.apply(null,arguments);return true}function j(e,r){for(var t=r;t;t=t.next)if(t.name==e)return true;return false}function T(r){var t=V.state;V.marked="def";if(t.context){if(t.lexical.info=="var"&&t.context&&t.context.block){var n=_(r,t.context);if(n!=null){t.context=n;return}}else if(!j(r,t.localVars)){t.localVars=new q(r,t.localVars);return}}if(e.globalVars&&!j(r,t.globalVars))t.globalVars=new q(r,t.globalVars)}function _(e,r){if(!r){return null}else if(r.block){var t=_(e,r.prev);if(!t)return null;if(t==r.prev)return r;return new O(t,r.vars,true)}else if(j(e,r.vars)){return r}else{return new O(r.prev,new q(e,r.vars),false)}}function $(e){return e=="public"||e=="private"||e=="protected"||e=="abstract"||e=="readonly"}function O(e,r,t){this.prev=e;this.vars=r;this.block=t}function q(e,r){this.name=e;this.next=r}var E=new q("this",new q("arguments",null));function I(){V.state.context=new O(V.state.context,V.state.localVars,false);V.state.localVars=E}function C(){V.state.context=new O(V.state.context,V.state.localVars,true);V.state.localVars=null}I.lex=C.lex=true;function S(){V.state.localVars=V.state.context.vars;V.state.context=V.state.context.prev}S.lex=true;function N(e,r){var t=function(){var t=V.state,n=t.indented;if(t.lexical.type=="stat")n=t.lexical.indented;else for(var i=t.lexical;i&&i.type==")"&&i.align;i=i.prev)n=i.indented;t.lexical=new h(n,V.stream.column(),e,null,t.lexical,r)};t.lex=true;return t}function P(){var e=V.state;if(e.lexical.prev){if(e.lexical.type==")")e.indented=e.lexical.indented;e.lexical=e.lexical.prev}}P.lex=true;function W(e){function r(t){if(t==e)return z();else if(e==";"||t=="}"||t==")"||t=="]")return A();else return z(r)}return r}function B(e,r){if(e=="var")return z(N("vardef",r),Ae,W(";"),P);if(e=="keyword a")return z(N("form"),G,B,P);if(e=="keyword b")return z(N("form"),B,P);if(e=="keyword d")return V.stream.match(/^\s*$/,false)?z():z(N("stat"),J,W(";"),P);if(e=="debugger")return z(W(";"));if(e=="{")return z(N("}"),C,se,P,S);if(e==";")return z();if(e=="if"){if(V.state.lexical.info=="else"&&V.state.cc[V.state.cc.length-1]==P)V.state.cc.pop()();return z(N("form"),G,B,P,Oe)}if(e=="function")return z(Ce);if(e=="for")return z(N("form"),C,qe,B,S,P);if(e=="class"||i&&r=="interface"){V.marked="keyword";return z(N("form",e=="class"?e:r),Be,P)}if(e=="variable"){if(i&&r=="declare"){V.marked="keyword";return z(B)}else if(i&&(r=="module"||r=="enum"||r=="type")&&V.stream.match(/^\s*\w/,false)){V.marked="keyword";if(r=="enum")return z(Xe);else if(r=="type")return z(Ne,W("operator"),me,W(";"));else return z(N("form"),ze,W("{"),N("}"),se,P,P)}else if(i&&r=="namespace"){V.marked="keyword";return z(N("form"),F,B,P)}else if(i&&r=="abstract"){V.marked="keyword";return z(B)}else{return z(N("stat"),re)}}if(e=="switch")return z(N("form"),G,W("{"),N("}","switch"),C,se,P,P,S);if(e=="case")return z(F,W(":"));if(e=="default")return z(W(":"));if(e=="catch")return z(N("form"),I,D,B,P,S);if(e=="export")return z(N("stat"),Ge,P);if(e=="import")return z(N("stat"),Je,P);if(e=="async")return z(B);if(r=="@")return z(F,B);return A(N("stat"),F,W(";"),P)}function D(e){if(e=="(")return z(Pe,W(")"))}function F(e,r){return H(e,r,false)}function U(e,r){return H(e,r,true)}function G(e){if(e!="(")return A();return z(N(")"),J,W(")"),P)}function H(e,r,t){if(V.state.fatArrowAt==V.stream.start){var n=t?X:R;if(e=="(")return z(I,N(")"),ue(Pe,")"),P,W("=>"),n,S);else if(e=="variable")return A(I,ze,W("=>"),n,S)}var a=t?L:K;if(b.hasOwnProperty(e))return z(a);if(e=="function")return z(Ce,a);if(e=="class"||i&&r=="interface"){V.marked="keyword";return z(N("form"),We,P)}if(e=="keyword c"||e=="async")return z(t?U:F);if(e=="(")return z(N(")"),J,W(")"),P,a);if(e=="operator"||e=="spread")return z(t?U:F);if(e=="[")return z(N("]"),Re,P,a);if(e=="{")return fe(ne,"}",null,a);if(e=="quasi")return A(M,a);if(e=="new")return z(Y(t));return z()}function J(e){if(e.match(/[;\}\)\],]/))return A();return A(F)}function K(e,r){if(e==",")return z(J);return L(e,r,false)}function L(e,r,t){var n=t==false?K:L;var a=t==false?F:U;if(e=="=>")return z(I,t?X:R,S);if(e=="operator"){if(/\+\+|--/.test(r)||i&&r=="!")return z(n);if(i&&r=="<"&&V.stream.match(/^([^<>]|<[^<>]*>)*>\s*\(/,false))return z(N(">"),ue(me,">"),P,n);if(r=="?")return z(F,W(":"),a);return z(a)}if(e=="quasi"){return A(M,n)}if(e==";")return;if(e=="(")return fe(U,")","call",n);if(e==".")return z(te,n);if(e=="[")return z(N("]"),J,W("]"),P,n);if(i&&r=="as"){V.marked="keyword";return z(me,n)}if(e=="regexp"){V.state.lastType=V.marked="operator";V.stream.backUp(V.stream.pos-V.stream.start-1);return z(a)}}function M(e,r){if(e!="quasi")return A();if(r.slice(r.length-2)!="${")return z(M);return z(J,Q)}function Q(e){if(e=="}"){V.marked="string.special";V.state.tokenize=v;return z(M)}}function R(e){w(V.stream,V.state);return A(e=="{"?B:F)}function X(e){w(V.stream,V.state);return A(e=="{"?B:U)}function Y(e){return function(r){if(r==".")return z(e?ee:Z);else if(r=="variable"&&i)return z(xe,e?L:K);else return A(e?U:F)}}function Z(e,r){if(r=="target"){V.marked="keyword";return z(K)}}function ee(e,r){if(r=="target"){V.marked="keyword";return z(L)}}function re(e){if(e==":")return z(P,B);return A(K,W(";"),P)}function te(e){if(e=="variable"){V.marked="property";return z()}}function ne(e,r){if(e=="async"){V.marked="property";return z(ne)}else if(e=="variable"||V.style=="keyword"){V.marked="property";if(r=="get"||r=="set")return z(ie);var n;if(i&&V.state.fatArrowAt==V.stream.start&&(n=V.stream.match(/^\s*:\s*/,false)))V.state.fatArrowAt=V.stream.pos+n[0].length;return z(ae)}else if(e=="number"||e=="string"){V.marked=t?"property":V.style+" property";return z(ae)}else if(e=="jsonld-keyword"){return z(ae)}else if(i&&$(r)){V.marked="keyword";return z(ne)}else if(e=="["){return z(F,oe,W("]"),ae)}else if(e=="spread"){return z(U,ae)}else if(r=="*"){V.marked="keyword";return z(ne)}else if(e==":"){return A(ae)}}function ie(e){if(e!="variable")return A(ae);V.marked="property";return z(Ce)}function ae(e){if(e==":")return z(U);if(e=="(")return A(Ce)}function ue(e,r,t){function n(i,a){if(t?t.indexOf(i)>-1:i==","){var u=V.state.lexical;if(u.info=="call")u.pos=(u.pos||0)+1;return z((function(t,n){if(t==r||n==r)return A();return A(e)}),n)}if(i==r||a==r)return z();if(t&&t.indexOf(";")>-1)return A(e);return z(W(r))}return function(t,i){if(t==r||i==r)return z();return A(e,n)}}function fe(e,r,t){for(var n=3;n<arguments.length;n++)V.cc.push(arguments[n]);return z(N(r,t),ue(e,r),P)}function se(e){if(e=="}")return z();return A(B,se)}function oe(e,r){if(i){if(e==":")return z(me);if(r=="?")return z(oe)}}function le(e,r){if(i&&(e==":"||r=="in"))return z(me)}function ce(e){if(i&&e==":"){if(V.stream.match(/^\s*\w+\s+is\b/,false))return z(F,de,me);else return z(me)}}function de(e,r){if(r=="is"){V.marked="keyword";return z()}}function me(e,r){if(r=="keyof"||r=="typeof"||r=="infer"||r=="readonly"){V.marked="keyword";return z(r=="typeof"?U:me)}if(e=="variable"||r=="void"){V.marked="type";return z(he)}if(r=="|"||r=="&")return z(me);if(e=="string"||e=="number"||e=="atom")return z(he);if(e=="[")return z(N("]"),ue(me,"]",","),P,he);if(e=="{")return z(N("}"),ke,P,he);if(e=="(")return z(ue(be,")"),pe,he);if(e=="<")return z(ue(me,">"),me);if(e=="quasi")return A(ye,he)}function pe(e){if(e=="=>")return z(me)}function ke(e){if(e.match(/[\}\)\]]/))return z();if(e==","||e==";")return z(ke);return A(ve,ke)}function ve(e,r){if(e=="variable"||V.style=="keyword"){V.marked="property";return z(ve)}else if(r=="?"||e=="number"||e=="string"){return z(ve)}else if(e==":"){return z(me)}else if(e=="["){return z(W("variable"),le,W("]"),ve)}else if(e=="("){return A(Se,ve)}else if(!e.match(/[;\}\)\],]/)){return z()}}function ye(e,r){if(e!="quasi")return A();if(r.slice(r.length-2)!="${")return z(ye);return z(me,we)}function we(e){if(e=="}"){V.marked="string-2";V.state.tokenize=v;return z(ye)}}function be(e,r){if(e=="variable"&&V.stream.match(/^\s*[?:]/,false)||r=="?")return z(be);if(e==":")return z(me);if(e=="spread")return z(be);return A(me)}function he(e,r){if(r=="<")return z(N(">"),ue(me,">"),P,he);if(r=="|"||e=="."||r=="&")return z(me);if(e=="[")return z(me,W("]"),he);if(r=="extends"||r=="implements"){V.marked="keyword";return z(me)}if(r=="?")return z(me,W(":"),me)}function xe(e,r){if(r=="<")return z(N(">"),ue(me,">"),P,he)}function ge(){return A(me,Ve)}function Ve(e,r){if(r=="=")return z(me)}function Ae(e,r){if(r=="enum"){V.marked="keyword";return z(Xe)}return A(ze,oe,_e,$e)}function ze(e,r){if(i&&$(r)){V.marked="keyword";return z(ze)}if(e=="variable"){T(r);return z()}if(e=="spread")return z(ze);if(e=="[")return fe(Te,"]");if(e=="{")return fe(je,"}")}function je(e,r){if(e=="variable"&&!V.stream.match(/^\s*:/,false)){T(r);return z(_e)}if(e=="variable")V.marked="property";if(e=="spread")return z(ze);if(e=="}")return A();if(e=="[")return z(F,W("]"),W(":"),je);return z(W(":"),ze,_e)}function Te(){return A(ze,_e)}function _e(e,r){if(r=="=")return z(U)}function $e(e){if(e==",")return z(Ae)}function Oe(e,r){if(e=="keyword b"&&r=="else")return z(N("form","else"),B,P)}function qe(e,r){if(r=="await")return z(qe);if(e=="(")return z(N(")"),Ee,P)}function Ee(e){if(e=="var")return z(Ae,Ie);if(e=="variable")return z(Ie);return A(Ie)}function Ie(e,r){if(e==")")return z();if(e==";")return z(Ie);if(r=="in"||r=="of"){V.marked="keyword";return z(F,Ie)}return A(F,Ie)}function Ce(e,r){if(r=="*"){V.marked="keyword";return z(Ce)}if(e=="variable"){T(r);return z(Ce)}if(e=="(")return z(I,N(")"),ue(Pe,")"),P,ce,B,S);if(i&&r=="<")return z(N(">"),ue(ge,">"),P,Ce)}function Se(e,r){if(r=="*"){V.marked="keyword";return z(Se)}if(e=="variable"){T(r);return z(Se)}if(e=="(")return z(I,N(")"),ue(Pe,")"),P,ce,S);if(i&&r=="<")return z(N(">"),ue(ge,">"),P,Se)}function Ne(e,r){if(e=="keyword"||e=="variable"){V.marked="type";return z(Ne)}else if(r=="<"){return z(N(">"),ue(ge,">"),P)}}function Pe(e,r){if(r=="@")z(F,Pe);if(e=="spread")return z(Pe);if(i&&$(r)){V.marked="keyword";return z(Pe)}if(i&&e=="this")return z(oe,_e);return A(ze,oe,_e)}function We(e,r){if(e=="variable")return Be(e,r);return De(e,r)}function Be(e,r){if(e=="variable"){T(r);return z(De)}}function De(e,r){if(r=="<")return z(N(">"),ue(ge,">"),P,De);if(r=="extends"||r=="implements"||i&&e==","){if(r=="implements")V.marked="keyword";return z(i?me:F,De)}if(e=="{")return z(N("}"),Fe,P)}function Fe(e,r){if(e=="async"||e=="variable"&&(r=="static"||r=="get"||r=="set"||i&&$(r))&&V.stream.match(/^\s+#?[\w$\xa1-\uffff]/,false)){V.marked="keyword";return z(Fe)}if(e=="variable"||V.style=="keyword"){V.marked="property";return z(Ue,Fe)}if(e=="number"||e=="string")return z(Ue,Fe);if(e=="[")return z(F,oe,W("]"),Ue,Fe);if(r=="*"){V.marked="keyword";return z(Fe)}if(i&&e=="(")return A(Se,Fe);if(e==";"||e==",")return z(Fe);if(e=="}")return z();if(r=="@")return z(F,Fe)}function Ue(e,r){if(r=="!"||r=="?")return z(Ue);if(e==":")return z(me,_e);if(r=="=")return z(U);var t=V.state.lexical.prev,n=t&&t.info=="interface";return A(n?Se:Ce)}function Ge(e,r){if(r=="*"){V.marked="keyword";return z(Qe,W(";"))}if(r=="default"){V.marked="keyword";return z(F,W(";"))}if(e=="{")return z(ue(He,"}"),Qe,W(";"));return A(B)}function He(e,r){if(r=="as"){V.marked="keyword";return z(W("variable"))}if(e=="variable")return A(U,He)}function Je(e){if(e=="string")return z();if(e=="(")return A(F);if(e==".")return A(K);return A(Ke,Le,Qe)}function Ke(e,r){if(e=="{")return fe(Ke,"}");if(e=="variable")T(r);if(r=="*")V.marked="keyword";return z(Me)}function Le(e){if(e==",")return z(Ke,Le)}function Me(e,r){if(r=="as"){V.marked="keyword";return z(Ke)}}function Qe(e,r){if(r=="from"){V.marked="keyword";return z(F)}}function Re(e){if(e=="]")return z();return A(ue(U,"]"))}function Xe(){return A(N("form"),ze,W("{"),N("}"),ue(Ye,"}"),P,P)}function Ye(){return A(ze,_e)}function Ze(e,r){return e.lastType=="operator"||e.lastType==","||f.test(r.charAt(0))||/[,.]/.test(r.charAt(0))}function er(e,r,t){return r.tokenize==m&&/^(?:operator|sof|keyword [bcd]|case|new|export|default|spread|[\[{}\(,;:]|=>)$/.test(r.lastType)||r.lastType=="quasi"&&/\{\s*$/.test(e.string.slice(0,e.pos-(t||0)))}return{name:e.name,startState:function(r){var t={tokenize:m,lastType:"sof",cc:[],lexical:new h(-r,0,"block",false),localVars:e.localVars,context:e.localVars&&new O(null,null,false),indented:0};if(e.globalVars&&typeof e.globalVars=="object")t.globalVars=e.globalVars;return t},token:function(e,r){if(e.sol()){if(!r.lexical.hasOwnProperty("align"))r.lexical.align=false;r.indented=e.indentation();w(e,r)}if(r.tokenize!=k&&e.eatSpace())return null;var t=r.tokenize(e,r);if(l=="comment")return t;r.lastType=l=="operator"&&(c=="++"||c=="--")?"incdec":l;return g(r,t,l,c,e)},indent:function(t,n,i){if(t.tokenize==k||t.tokenize==v)return null;if(t.tokenize!=m)return 0;var a=n&&n.charAt(0),u=t.lexical,f;if(!/^\s*else\b/.test(n))for(var s=t.cc.length-1;s>=0;--s){var o=t.cc[s];if(o==P)u=u.prev;else if(o!=Oe&&o!=S)break}while((u.type=="stat"||u.type=="form")&&(a=="}"||(f=t.cc[t.cc.length-1])&&(f==K||f==L)&&!/^[,\.=+\-*:?[\(]/.test(n)))u=u.prev;if(r&&u.type==")"&&u.prev.type=="stat")u=u.prev;var l=u.type,c=a==l;if(l=="vardef")return u.indented+(t.lastType=="operator"||t.lastType==","?u.info.length+1:0);else if(l=="form"&&a=="{")return u.indented;else if(l=="form")return u.indented+i.unit;else if(l=="stat")return u.indented+(Ze(t,n)?r||i.unit:0);else if(u.info=="switch"&&!c&&e.doubleIndentSwitch!=false)return u.indented+(/^(?:case|default)\b/.test(n)?i.unit:2*i.unit);else if(u.align)return u.column+(c?0:1);else return u.indented+(c?0:i.unit)},languageData:{indentOnInput:/^\s*(?:case .*?:|default:|\{|\})$/,commentTokens:n?undefined:{line:"//",block:{open:"/*",close:"*/"}},closeBrackets:{brackets:["(","[","{","'",'"',"`"]},wordChars:"$"}}}const i=n({name:"javascript"});const a=n({name:"json",json:true});const u=n({name:"json",jsonld:true});const f=n({name:"typescript",typescript:true})}}]);