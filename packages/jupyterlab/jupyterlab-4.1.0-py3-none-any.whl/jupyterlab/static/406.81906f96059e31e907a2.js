"use strict";(self["webpackChunk_jupyterlab_application_top"]=self["webpackChunk_jupyterlab_application_top"]||[]).push([[406],{20406:(t,e,r)=>{r.r(e);r.d(e,{diagram:()=>lt});var n=r(23787);var i=r(67058);var a=r(34596);var s=r(96001);const o=[];for(let ht=0;ht<256;++ht){o.push((ht+256).toString(16).slice(1))}function c(t,e=0){return(o[t[e+0]]+o[t[e+1]]+o[t[e+2]]+o[t[e+3]]+"-"+o[t[e+4]]+o[t[e+5]]+"-"+o[t[e+6]]+o[t[e+7]]+"-"+o[t[e+8]]+o[t[e+9]]+"-"+o[t[e+10]]+o[t[e+11]]+o[t[e+12]]+o[t[e+13]]+o[t[e+14]]+o[t[e+15]]).toLowerCase()}function l(t,e=0){const r=c(t,e);if(!validate(r)){throw TypeError("Stringified UUID is invalid")}return r}const h=null&&l;const d=/^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000)$/i;function u(t){return typeof t==="string"&&d.test(t)}const y=u;function f(t){if(!y(t)){throw TypeError("Invalid UUID")}let e;const r=new Uint8Array(16);r[0]=(e=parseInt(t.slice(0,8),16))>>>24;r[1]=e>>>16&255;r[2]=e>>>8&255;r[3]=e&255;r[4]=(e=parseInt(t.slice(9,13),16))>>>8;r[5]=e&255;r[6]=(e=parseInt(t.slice(14,18),16))>>>8;r[7]=e&255;r[8]=(e=parseInt(t.slice(19,23),16))>>>8;r[9]=e&255;r[10]=(e=parseInt(t.slice(24,36),16))/1099511627776&255;r[11]=e/4294967296&255;r[12]=e>>>24&255;r[13]=e>>>16&255;r[14]=e>>>8&255;r[15]=e&255;return r}const p=f;function _(t){t=unescape(encodeURIComponent(t));const e=[];for(let r=0;r<t.length;++r){e.push(t.charCodeAt(r))}return e}const E="6ba7b810-9dad-11d1-80b4-00c04fd430c8";const m="6ba7b811-9dad-11d1-80b4-00c04fd430c8";function g(t,e,r){function n(t,n,i,a){var s;if(typeof t==="string"){t=_(t)}if(typeof n==="string"){n=p(n)}if(((s=n)===null||s===void 0?void 0:s.length)!==16){throw TypeError("Namespace must be array-like (16 iterable integer values, 0-255)")}let o=new Uint8Array(16+t.length);o.set(n);o.set(t,n.length);o=r(o);o[6]=o[6]&15|e;o[8]=o[8]&63|128;if(i){a=a||0;for(let t=0;t<16;++t){i[a+t]=o[t]}return i}return c(o)}try{n.name=t}catch(i){}n.DNS=E;n.URL=m;return n}function b(t,e,r,n){switch(t){case 0:return e&r^~e&n;case 1:return e^r^n;case 2:return e&r^e&n^r&n;case 3:return e^r^n}}function k(t,e){return t<<e|t>>>32-e}function O(t){const e=[1518500249,1859775393,2400959708,3395469782];const r=[1732584193,4023233417,2562383102,271733878,3285377520];if(typeof t==="string"){const e=unescape(encodeURIComponent(t));t=[];for(let r=0;r<e.length;++r){t.push(e.charCodeAt(r))}}else if(!Array.isArray(t)){t=Array.prototype.slice.call(t)}t.push(128);const n=t.length/4+2;const i=Math.ceil(n/16);const a=new Array(i);for(let s=0;s<i;++s){const e=new Uint32Array(16);for(let r=0;r<16;++r){e[r]=t[s*64+r*4]<<24|t[s*64+r*4+1]<<16|t[s*64+r*4+2]<<8|t[s*64+r*4+3]}a[s]=e}a[i-1][14]=(t.length-1)*8/Math.pow(2,32);a[i-1][14]=Math.floor(a[i-1][14]);a[i-1][15]=(t.length-1)*8&4294967295;for(let s=0;s<i;++s){const t=new Uint32Array(80);for(let e=0;e<16;++e){t[e]=a[s][e]}for(let e=16;e<80;++e){t[e]=k(t[e-3]^t[e-8]^t[e-14]^t[e-16],1)}let n=r[0];let i=r[1];let o=r[2];let c=r[3];let l=r[4];for(let r=0;r<80;++r){const a=Math.floor(r/20);const s=k(n,5)+b(a,i,o,c)+l+e[a]+t[r]>>>0;l=c;c=o;o=k(i,30)>>>0;i=n;n=s}r[0]=r[0]+n>>>0;r[1]=r[1]+i>>>0;r[2]=r[2]+o>>>0;r[3]=r[3]+c>>>0;r[4]=r[4]+l>>>0}return[r[0]>>24&255,r[0]>>16&255,r[0]>>8&255,r[0]&255,r[1]>>24&255,r[1]>>16&255,r[1]>>8&255,r[1]&255,r[2]>>24&255,r[2]>>16&255,r[2]>>8&255,r[2]&255,r[3]>>24&255,r[3]>>16&255,r[3]>>8&255,r[3]&255,r[4]>>24&255,r[4]>>16&255,r[4]>>8&255,r[4]&255]}const R=O;const N=g("v5",80,R);const T=N;var x=r(27484);var A=r(17967);var M=r(27856);var v=function(){var t=function(t,e,r,n){for(r=r||{},n=t.length;n--;r[t[n]]=e);return r},e=[6,8,10,20,22,24,26,27,28],r=[1,10],n=[1,11],i=[1,12],a=[1,13],s=[1,14],o=[1,15],c=[1,21],l=[1,22],h=[1,23],d=[1,24],u=[1,25],y=[6,8,10,13,15,18,19,20,22,24,26,27,28,41,42,43,44,45],f=[1,34],p=[27,28,46,47],_=[41,42,43,44,45],E=[17,34],m=[1,54],g=[1,53],b=[17,34,36,38];var k={trace:function t(){},yy:{},symbols_:{error:2,start:3,ER_DIAGRAM:4,document:5,EOF:6,line:7,SPACE:8,statement:9,NEWLINE:10,entityName:11,relSpec:12,":":13,role:14,BLOCK_START:15,attributes:16,BLOCK_STOP:17,SQS:18,SQE:19,title:20,title_value:21,acc_title:22,acc_title_value:23,acc_descr:24,acc_descr_value:25,acc_descr_multiline_value:26,ALPHANUM:27,ENTITY_NAME:28,attribute:29,attributeType:30,attributeName:31,attributeKeyTypeList:32,attributeComment:33,ATTRIBUTE_WORD:34,attributeKeyType:35,COMMA:36,ATTRIBUTE_KEY:37,COMMENT:38,cardinality:39,relType:40,ZERO_OR_ONE:41,ZERO_OR_MORE:42,ONE_OR_MORE:43,ONLY_ONE:44,MD_PARENT:45,NON_IDENTIFYING:46,IDENTIFYING:47,WORD:48,$accept:0,$end:1},terminals_:{2:"error",4:"ER_DIAGRAM",6:"EOF",8:"SPACE",10:"NEWLINE",13:":",15:"BLOCK_START",17:"BLOCK_STOP",18:"SQS",19:"SQE",20:"title",21:"title_value",22:"acc_title",23:"acc_title_value",24:"acc_descr",25:"acc_descr_value",26:"acc_descr_multiline_value",27:"ALPHANUM",28:"ENTITY_NAME",34:"ATTRIBUTE_WORD",36:"COMMA",37:"ATTRIBUTE_KEY",38:"COMMENT",41:"ZERO_OR_ONE",42:"ZERO_OR_MORE",43:"ONE_OR_MORE",44:"ONLY_ONE",45:"MD_PARENT",46:"NON_IDENTIFYING",47:"IDENTIFYING",48:"WORD"},productions_:[0,[3,3],[5,0],[5,2],[7,2],[7,1],[7,1],[7,1],[9,5],[9,4],[9,3],[9,1],[9,7],[9,6],[9,4],[9,2],[9,2],[9,2],[9,1],[11,1],[11,1],[16,1],[16,2],[29,2],[29,3],[29,3],[29,4],[30,1],[31,1],[32,1],[32,3],[35,1],[33,1],[12,3],[39,1],[39,1],[39,1],[39,1],[39,1],[40,1],[40,1],[14,1],[14,1],[14,1]],performAction:function t(e,r,n,i,a,s,o){var c=s.length-1;switch(a){case 1:break;case 2:this.$=[];break;case 3:s[c-1].push(s[c]);this.$=s[c-1];break;case 4:case 5:this.$=s[c];break;case 6:case 7:this.$=[];break;case 8:i.addEntity(s[c-4]);i.addEntity(s[c-2]);i.addRelationship(s[c-4],s[c],s[c-2],s[c-3]);break;case 9:i.addEntity(s[c-3]);i.addAttributes(s[c-3],s[c-1]);break;case 10:i.addEntity(s[c-2]);break;case 11:i.addEntity(s[c]);break;case 12:i.addEntity(s[c-6],s[c-4]);i.addAttributes(s[c-6],s[c-1]);break;case 13:i.addEntity(s[c-5],s[c-3]);break;case 14:i.addEntity(s[c-3],s[c-1]);break;case 15:case 16:this.$=s[c].trim();i.setAccTitle(this.$);break;case 17:case 18:this.$=s[c].trim();i.setAccDescription(this.$);break;case 19:case 43:this.$=s[c];break;case 20:case 41:case 42:this.$=s[c].replace(/"/g,"");break;case 21:case 29:this.$=[s[c]];break;case 22:s[c].push(s[c-1]);this.$=s[c];break;case 23:this.$={attributeType:s[c-1],attributeName:s[c]};break;case 24:this.$={attributeType:s[c-2],attributeName:s[c-1],attributeKeyTypeList:s[c]};break;case 25:this.$={attributeType:s[c-2],attributeName:s[c-1],attributeComment:s[c]};break;case 26:this.$={attributeType:s[c-3],attributeName:s[c-2],attributeKeyTypeList:s[c-1],attributeComment:s[c]};break;case 27:case 28:case 31:this.$=s[c];break;case 30:s[c-2].push(s[c]);this.$=s[c-2];break;case 32:this.$=s[c].replace(/"/g,"");break;case 33:this.$={cardA:s[c],relType:s[c-1],cardB:s[c-2]};break;case 34:this.$=i.Cardinality.ZERO_OR_ONE;break;case 35:this.$=i.Cardinality.ZERO_OR_MORE;break;case 36:this.$=i.Cardinality.ONE_OR_MORE;break;case 37:this.$=i.Cardinality.ONLY_ONE;break;case 38:this.$=i.Cardinality.MD_PARENT;break;case 39:this.$=i.Identification.NON_IDENTIFYING;break;case 40:this.$=i.Identification.IDENTIFYING;break}},table:[{3:1,4:[1,2]},{1:[3]},t(e,[2,2],{5:3}),{6:[1,4],7:5,8:[1,6],9:7,10:[1,8],11:9,20:r,22:n,24:i,26:a,27:s,28:o},t(e,[2,7],{1:[2,1]}),t(e,[2,3]),{9:16,11:9,20:r,22:n,24:i,26:a,27:s,28:o},t(e,[2,5]),t(e,[2,6]),t(e,[2,11],{12:17,39:20,15:[1,18],18:[1,19],41:c,42:l,43:h,44:d,45:u}),{21:[1,26]},{23:[1,27]},{25:[1,28]},t(e,[2,18]),t(y,[2,19]),t(y,[2,20]),t(e,[2,4]),{11:29,27:s,28:o},{16:30,17:[1,31],29:32,30:33,34:f},{11:35,27:s,28:o},{40:36,46:[1,37],47:[1,38]},t(p,[2,34]),t(p,[2,35]),t(p,[2,36]),t(p,[2,37]),t(p,[2,38]),t(e,[2,15]),t(e,[2,16]),t(e,[2,17]),{13:[1,39]},{17:[1,40]},t(e,[2,10]),{16:41,17:[2,21],29:32,30:33,34:f},{31:42,34:[1,43]},{34:[2,27]},{19:[1,44]},{39:45,41:c,42:l,43:h,44:d,45:u},t(_,[2,39]),t(_,[2,40]),{14:46,27:[1,49],28:[1,48],48:[1,47]},t(e,[2,9]),{17:[2,22]},t(E,[2,23],{32:50,33:51,35:52,37:m,38:g}),t([17,34,37,38],[2,28]),t(e,[2,14],{15:[1,55]}),t([27,28],[2,33]),t(e,[2,8]),t(e,[2,41]),t(e,[2,42]),t(e,[2,43]),t(E,[2,24],{33:56,36:[1,57],38:g}),t(E,[2,25]),t(b,[2,29]),t(E,[2,32]),t(b,[2,31]),{16:58,17:[1,59],29:32,30:33,34:f},t(E,[2,26]),{35:60,37:m},{17:[1,61]},t(e,[2,13]),t(b,[2,30]),t(e,[2,12])],defaultActions:{34:[2,27],41:[2,22]},parseError:function t(e,r){if(r.recoverable){this.trace(e)}else{var n=new Error(e);n.hash=r;throw n}},parse:function t(e){var r=this,n=[0],i=[],a=[null],s=[],o=this.table,c="",l=0,h=0,d=2,u=1;var y=s.slice.call(arguments,1);var f=Object.create(this.lexer);var p={yy:{}};for(var _ in this.yy){if(Object.prototype.hasOwnProperty.call(this.yy,_)){p.yy[_]=this.yy[_]}}f.setInput(e,p.yy);p.yy.lexer=f;p.yy.parser=this;if(typeof f.yylloc=="undefined"){f.yylloc={}}var E=f.yylloc;s.push(E);var m=f.options&&f.options.ranges;if(typeof p.yy.parseError==="function"){this.parseError=p.yy.parseError}else{this.parseError=Object.getPrototypeOf(this).parseError}function g(){var t;t=i.pop()||f.lex()||u;if(typeof t!=="number"){if(t instanceof Array){i=t;t=i.pop()}t=r.symbols_[t]||t}return t}var b,k,O,R,N={},T,x,A,M;while(true){k=n[n.length-1];if(this.defaultActions[k]){O=this.defaultActions[k]}else{if(b===null||typeof b=="undefined"){b=g()}O=o[k]&&o[k][b]}if(typeof O==="undefined"||!O.length||!O[0]){var v="";M=[];for(T in o[k]){if(this.terminals_[T]&&T>d){M.push("'"+this.terminals_[T]+"'")}}if(f.showPosition){v="Parse error on line "+(l+1)+":\n"+f.showPosition()+"\nExpecting "+M.join(", ")+", got '"+(this.terminals_[b]||b)+"'"}else{v="Parse error on line "+(l+1)+": Unexpected "+(b==u?"end of input":"'"+(this.terminals_[b]||b)+"'")}this.parseError(v,{text:f.match,token:this.terminals_[b]||b,line:f.yylineno,loc:E,expected:M})}if(O[0]instanceof Array&&O.length>1){throw new Error("Parse Error: multiple actions possible at state: "+k+", token: "+b)}switch(O[0]){case 1:n.push(b);a.push(f.yytext);s.push(f.yylloc);n.push(O[1]);b=null;{h=f.yyleng;c=f.yytext;l=f.yylineno;E=f.yylloc}break;case 2:x=this.productions_[O[1]][1];N.$=a[a.length-x];N._$={first_line:s[s.length-(x||1)].first_line,last_line:s[s.length-1].last_line,first_column:s[s.length-(x||1)].first_column,last_column:s[s.length-1].last_column};if(m){N._$.range=[s[s.length-(x||1)].range[0],s[s.length-1].range[1]]}R=this.performAction.apply(N,[c,h,l,p.yy,O[1],a,s].concat(y));if(typeof R!=="undefined"){return R}if(x){n=n.slice(0,-1*x*2);a=a.slice(0,-1*x);s=s.slice(0,-1*x)}n.push(this.productions_[O[1]][0]);a.push(N.$);s.push(N._$);A=o[n[n.length-2]][n[n.length-1]];n.push(A);break;case 3:return true}}return true}};var O=function(){var t={EOF:1,parseError:function t(e,r){if(this.yy.parser){this.yy.parser.parseError(e,r)}else{throw new Error(e)}},setInput:function(t,e){this.yy=e||this.yy||{};this._input=t;this._more=this._backtrack=this.done=false;this.yylineno=this.yyleng=0;this.yytext=this.matched=this.match="";this.conditionStack=["INITIAL"];this.yylloc={first_line:1,first_column:0,last_line:1,last_column:0};if(this.options.ranges){this.yylloc.range=[0,0]}this.offset=0;return this},input:function(){var t=this._input[0];this.yytext+=t;this.yyleng++;this.offset++;this.match+=t;this.matched+=t;var e=t.match(/(?:\r\n?|\n).*/g);if(e){this.yylineno++;this.yylloc.last_line++}else{this.yylloc.last_column++}if(this.options.ranges){this.yylloc.range[1]++}this._input=this._input.slice(1);return t},unput:function(t){var e=t.length;var r=t.split(/(?:\r\n?|\n)/g);this._input=t+this._input;this.yytext=this.yytext.substr(0,this.yytext.length-e);this.offset-=e;var n=this.match.split(/(?:\r\n?|\n)/g);this.match=this.match.substr(0,this.match.length-1);this.matched=this.matched.substr(0,this.matched.length-1);if(r.length-1){this.yylineno-=r.length-1}var i=this.yylloc.range;this.yylloc={first_line:this.yylloc.first_line,last_line:this.yylineno+1,first_column:this.yylloc.first_column,last_column:r?(r.length===n.length?this.yylloc.first_column:0)+n[n.length-r.length].length-r[0].length:this.yylloc.first_column-e};if(this.options.ranges){this.yylloc.range=[i[0],i[0]+this.yyleng-e]}this.yyleng=this.yytext.length;return this},more:function(){this._more=true;return this},reject:function(){if(this.options.backtrack_lexer){this._backtrack=true}else{return this.parseError("Lexical error on line "+(this.yylineno+1)+". You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).\n"+this.showPosition(),{text:"",token:null,line:this.yylineno})}return this},less:function(t){this.unput(this.match.slice(t))},pastInput:function(){var t=this.matched.substr(0,this.matched.length-this.match.length);return(t.length>20?"...":"")+t.substr(-20).replace(/\n/g,"")},upcomingInput:function(){var t=this.match;if(t.length<20){t+=this._input.substr(0,20-t.length)}return(t.substr(0,20)+(t.length>20?"...":"")).replace(/\n/g,"")},showPosition:function(){var t=this.pastInput();var e=new Array(t.length+1).join("-");return t+this.upcomingInput()+"\n"+e+"^"},test_match:function(t,e){var r,n,i;if(this.options.backtrack_lexer){i={yylineno:this.yylineno,yylloc:{first_line:this.yylloc.first_line,last_line:this.last_line,first_column:this.yylloc.first_column,last_column:this.yylloc.last_column},yytext:this.yytext,match:this.match,matches:this.matches,matched:this.matched,yyleng:this.yyleng,offset:this.offset,_more:this._more,_input:this._input,yy:this.yy,conditionStack:this.conditionStack.slice(0),done:this.done};if(this.options.ranges){i.yylloc.range=this.yylloc.range.slice(0)}}n=t[0].match(/(?:\r\n?|\n).*/g);if(n){this.yylineno+=n.length}this.yylloc={first_line:this.yylloc.last_line,last_line:this.yylineno+1,first_column:this.yylloc.last_column,last_column:n?n[n.length-1].length-n[n.length-1].match(/\r?\n?/)[0].length:this.yylloc.last_column+t[0].length};this.yytext+=t[0];this.match+=t[0];this.matches=t;this.yyleng=this.yytext.length;if(this.options.ranges){this.yylloc.range=[this.offset,this.offset+=this.yyleng]}this._more=false;this._backtrack=false;this._input=this._input.slice(t[0].length);this.matched+=t[0];r=this.performAction.call(this,this.yy,this,e,this.conditionStack[this.conditionStack.length-1]);if(this.done&&this._input){this.done=false}if(r){return r}else if(this._backtrack){for(var a in i){this[a]=i[a]}return false}return false},next:function(){if(this.done){return this.EOF}if(!this._input){this.done=true}var t,e,r,n;if(!this._more){this.yytext="";this.match=""}var i=this._currentRules();for(var a=0;a<i.length;a++){r=this._input.match(this.rules[i[a]]);if(r&&(!e||r[0].length>e[0].length)){e=r;n=a;if(this.options.backtrack_lexer){t=this.test_match(r,i[a]);if(t!==false){return t}else if(this._backtrack){e=false;continue}else{return false}}else if(!this.options.flex){break}}}if(e){t=this.test_match(e,i[n]);if(t!==false){return t}return false}if(this._input===""){return this.EOF}else{return this.parseError("Lexical error on line "+(this.yylineno+1)+". Unrecognized text.\n"+this.showPosition(),{text:"",token:null,line:this.yylineno})}},lex:function t(){var e=this.next();if(e){return e}else{return this.lex()}},begin:function t(e){this.conditionStack.push(e)},popState:function t(){var e=this.conditionStack.length-1;if(e>0){return this.conditionStack.pop()}else{return this.conditionStack[0]}},_currentRules:function t(){if(this.conditionStack.length&&this.conditionStack[this.conditionStack.length-1]){return this.conditions[this.conditionStack[this.conditionStack.length-1]].rules}else{return this.conditions["INITIAL"].rules}},topState:function t(e){e=this.conditionStack.length-1-Math.abs(e||0);if(e>=0){return this.conditionStack[e]}else{return"INITIAL"}},pushState:function t(e){this.begin(e)},stateStackSize:function t(){return this.conditionStack.length},options:{"case-insensitive":true},performAction:function t(e,r,n,i){switch(n){case 0:this.begin("acc_title");return 22;case 1:this.popState();return"acc_title_value";case 2:this.begin("acc_descr");return 24;case 3:this.popState();return"acc_descr_value";case 4:this.begin("acc_descr_multiline");break;case 5:this.popState();break;case 6:return"acc_descr_multiline_value";case 7:return 10;case 8:break;case 9:return 8;case 10:return 28;case 11:return 48;case 12:return 4;case 13:this.begin("block");return 15;case 14:return 36;case 15:break;case 16:return 37;case 17:return 34;case 18:return 34;case 19:return 38;case 20:break;case 21:this.popState();return 17;case 22:return r.yytext[0];case 23:return 18;case 24:return 19;case 25:return 41;case 26:return 43;case 27:return 43;case 28:return 43;case 29:return 41;case 30:return 41;case 31:return 42;case 32:return 42;case 33:return 42;case 34:return 42;case 35:return 42;case 36:return 43;case 37:return 42;case 38:return 43;case 39:return 44;case 40:return 44;case 41:return 44;case 42:return 44;case 43:return 41;case 44:return 42;case 45:return 43;case 46:return 45;case 47:return 46;case 48:return 47;case 49:return 47;case 50:return 46;case 51:return 46;case 52:return 46;case 53:return 27;case 54:return r.yytext[0];case 55:return 6}},rules:[/^(?:accTitle\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*\{\s*)/i,/^(?:[\}])/i,/^(?:[^\}]*)/i,/^(?:[\n]+)/i,/^(?:\s+)/i,/^(?:[\s]+)/i,/^(?:"[^"%\r\n\v\b\\]+")/i,/^(?:"[^"]*")/i,/^(?:erDiagram\b)/i,/^(?:\{)/i,/^(?:,)/i,/^(?:\s+)/i,/^(?:\b((?:PK)|(?:FK)|(?:UK))\b)/i,/^(?:(.*?)[~](.*?)*[~])/i,/^(?:[\*A-Za-z_][A-Za-z0-9\-_\[\]\(\)]*)/i,/^(?:"[^"]*")/i,/^(?:[\n]+)/i,/^(?:\})/i,/^(?:.)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:one or zero\b)/i,/^(?:one or more\b)/i,/^(?:one or many\b)/i,/^(?:1\+)/i,/^(?:\|o\b)/i,/^(?:zero or one\b)/i,/^(?:zero or more\b)/i,/^(?:zero or many\b)/i,/^(?:0\+)/i,/^(?:\}o\b)/i,/^(?:many\(0\))/i,/^(?:many\(1\))/i,/^(?:many\b)/i,/^(?:\}\|)/i,/^(?:one\b)/i,/^(?:only one\b)/i,/^(?:1\b)/i,/^(?:\|\|)/i,/^(?:o\|)/i,/^(?:o\{)/i,/^(?:\|\{)/i,/^(?:\s*u\b)/i,/^(?:\.\.)/i,/^(?:--)/i,/^(?:to\b)/i,/^(?:optionally to\b)/i,/^(?:\.-)/i,/^(?:-\.)/i,/^(?:[A-Za-z_][A-Za-z0-9\-_]*)/i,/^(?:.)/i,/^(?:$)/i],conditions:{acc_descr_multiline:{rules:[5,6],inclusive:false},acc_descr:{rules:[3],inclusive:false},acc_title:{rules:[1],inclusive:false},block:{rules:[14,15,16,17,18,19,20,21,22],inclusive:false},INITIAL:{rules:[0,2,4,7,8,9,10,11,12,13,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55],inclusive:true}}};return t}();k.lexer=O;function R(){this.yy={}}R.prototype=k;k.Parser=R;return new R}();v.parser=v;const w=v;let I={};let D=[];const S={ZERO_OR_ONE:"ZERO_OR_ONE",ZERO_OR_MORE:"ZERO_OR_MORE",ONE_OR_MORE:"ONE_OR_MORE",ONLY_ONE:"ONLY_ONE",MD_PARENT:"MD_PARENT"};const $={NON_IDENTIFYING:"NON_IDENTIFYING",IDENTIFYING:"IDENTIFYING"};const L=function(t,e=void 0){if(I[t]===void 0){I[t]={attributes:[],alias:e};n.l.info("Added new entity :",t)}else if(I[t]&&!I[t].alias&&e){I[t].alias=e;n.l.info(`Add alias '${e}' to entity '${t}'`)}return I[t]};const C=()=>I;const B=function(t,e){let r=L(t);let i;for(i=e.length-1;i>=0;i--){r.attributes.push(e[i]);n.l.debug("Added attribute ",e[i].attributeName)}};const Y=function(t,e,r,i){let a={entityA:t,roleA:e,entityB:r,relSpec:i};D.push(a);n.l.debug("Added new relationship :",a)};const P=()=>D;const Z=function(){I={};D=[];(0,n.t)()};const F={Cardinality:S,Identification:$,getConfig:()=>(0,n.c)().er,addEntity:L,addAttributes:B,getEntities:C,addRelationship:Y,getRelationships:P,clear:Z,setAccTitle:n.s,getAccTitle:n.g,setAccDescription:n.b,getAccDescription:n.a,setDiagramTitle:n.q,getDiagramTitle:n.r};const z={ONLY_ONE_START:"ONLY_ONE_START",ONLY_ONE_END:"ONLY_ONE_END",ZERO_OR_ONE_START:"ZERO_OR_ONE_START",ZERO_OR_ONE_END:"ZERO_OR_ONE_END",ONE_OR_MORE_START:"ONE_OR_MORE_START",ONE_OR_MORE_END:"ONE_OR_MORE_END",ZERO_OR_MORE_START:"ZERO_OR_MORE_START",ZERO_OR_MORE_END:"ZERO_OR_MORE_END",MD_PARENT_END:"MD_PARENT_END",MD_PARENT_START:"MD_PARENT_START"};const U=function(t,e){let r;t.append("defs").append("marker").attr("id",z.MD_PARENT_START).attr("refX",0).attr("refY",7).attr("markerWidth",190).attr("markerHeight",240).attr("orient","auto").append("path").attr("d","M 18,7 L9,13 L1,7 L9,1 Z");t.append("defs").append("marker").attr("id",z.MD_PARENT_END).attr("refX",19).attr("refY",7).attr("markerWidth",20).attr("markerHeight",28).attr("orient","auto").append("path").attr("d","M 18,7 L9,13 L1,7 L9,1 Z");t.append("defs").append("marker").attr("id",z.ONLY_ONE_START).attr("refX",0).attr("refY",9).attr("markerWidth",18).attr("markerHeight",18).attr("orient","auto").append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M9,0 L9,18 M15,0 L15,18");t.append("defs").append("marker").attr("id",z.ONLY_ONE_END).attr("refX",18).attr("refY",9).attr("markerWidth",18).attr("markerHeight",18).attr("orient","auto").append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M3,0 L3,18 M9,0 L9,18");r=t.append("defs").append("marker").attr("id",z.ZERO_OR_ONE_START).attr("refX",0).attr("refY",9).attr("markerWidth",30).attr("markerHeight",18).attr("orient","auto");r.append("circle").attr("stroke",e.stroke).attr("fill","white").attr("cx",21).attr("cy",9).attr("r",6);r.append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M9,0 L9,18");r=t.append("defs").append("marker").attr("id",z.ZERO_OR_ONE_END).attr("refX",30).attr("refY",9).attr("markerWidth",30).attr("markerHeight",18).attr("orient","auto");r.append("circle").attr("stroke",e.stroke).attr("fill","white").attr("cx",9).attr("cy",9).attr("r",6);r.append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M21,0 L21,18");t.append("defs").append("marker").attr("id",z.ONE_OR_MORE_START).attr("refX",18).attr("refY",18).attr("markerWidth",45).attr("markerHeight",36).attr("orient","auto").append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M0,18 Q 18,0 36,18 Q 18,36 0,18 M42,9 L42,27");t.append("defs").append("marker").attr("id",z.ONE_OR_MORE_END).attr("refX",27).attr("refY",18).attr("markerWidth",45).attr("markerHeight",36).attr("orient","auto").append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M3,9 L3,27 M9,18 Q27,0 45,18 Q27,36 9,18");r=t.append("defs").append("marker").attr("id",z.ZERO_OR_MORE_START).attr("refX",18).attr("refY",18).attr("markerWidth",57).attr("markerHeight",36).attr("orient","auto");r.append("circle").attr("stroke",e.stroke).attr("fill","white").attr("cx",48).attr("cy",18).attr("r",6);r.append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M0,18 Q18,0 36,18 Q18,36 0,18");r=t.append("defs").append("marker").attr("id",z.ZERO_OR_MORE_END).attr("refX",39).attr("refY",18).attr("markerWidth",57).attr("markerHeight",36).attr("orient","auto");r.append("circle").attr("stroke",e.stroke).attr("fill","white").attr("cx",9).attr("cy",18).attr("r",6);r.append("path").attr("stroke",e.stroke).attr("fill","none").attr("d","M21,18 Q39,0 57,18 Q39,36 21,18");return};const W={ERMarkers:z,insertMarkers:U};const K=/[^\dA-Za-z](\W)*/g;let G={};let H=new Map;const j=function(t){const e=Object.keys(t);for(const r of e){G[r]=t[r]}};const Q=(t,e,r)=>{const i=G.entityPadding/3;const a=G.entityPadding/3;const s=G.fontSize*.85;const o=e.node().getBBox();const c=[];let l=false;let h=false;let d=0;let u=0;let y=0;let f=0;let p=o.height+i*2;let _=1;r.forEach((t=>{if(t.attributeKeyTypeList!==void 0&&t.attributeKeyTypeList.length>0){l=true}if(t.attributeComment!==void 0){h=true}}));r.forEach((r=>{const a=`${e.node().id}-attr-${_}`;let o=0;const E=(0,n.v)(r.attributeType);const m=t.append("text").classed("er entityLabel",true).attr("id",`${a}-type`).attr("x",0).attr("y",0).style("dominant-baseline","middle").style("text-anchor","left").style("font-family",(0,n.c)().fontFamily).style("font-size",s+"px").text(E);const g=t.append("text").classed("er entityLabel",true).attr("id",`${a}-name`).attr("x",0).attr("y",0).style("dominant-baseline","middle").style("text-anchor","left").style("font-family",(0,n.c)().fontFamily).style("font-size",s+"px").text(r.attributeName);const b={};b.tn=m;b.nn=g;const k=m.node().getBBox();const O=g.node().getBBox();d=Math.max(d,k.width);u=Math.max(u,O.width);o=Math.max(k.height,O.height);if(l){const e=r.attributeKeyTypeList!==void 0?r.attributeKeyTypeList.join(","):"";const i=t.append("text").classed("er entityLabel",true).attr("id",`${a}-key`).attr("x",0).attr("y",0).style("dominant-baseline","middle").style("text-anchor","left").style("font-family",(0,n.c)().fontFamily).style("font-size",s+"px").text(e);b.kn=i;const c=i.node().getBBox();y=Math.max(y,c.width);o=Math.max(o,c.height)}if(h){const e=t.append("text").classed("er entityLabel",true).attr("id",`${a}-comment`).attr("x",0).attr("y",0).style("dominant-baseline","middle").style("text-anchor","left").style("font-family",(0,n.c)().fontFamily).style("font-size",s+"px").text(r.attributeComment||"");b.cn=e;const i=e.node().getBBox();f=Math.max(f,i.width);o=Math.max(o,i.height)}b.height=o;c.push(b);p+=o+i*2;_+=1}));let E=4;if(l){E+=2}if(h){E+=2}const m=d+u+y+f;const g={width:Math.max(G.minEntityWidth,Math.max(o.width+G.entityPadding*2,m+a*E)),height:r.length>0?p:Math.max(G.minEntityHeight,o.height+G.entityPadding*2)};if(r.length>0){const r=Math.max(0,(g.width-m-a*E)/(E/2));e.attr("transform","translate("+g.width/2+","+(i+o.height/2)+")");let n=o.height+i*2;let s="attributeBoxOdd";c.forEach((e=>{const o=n+i+e.height/2;e.tn.attr("transform","translate("+a+","+o+")");const c=t.insert("rect","#"+e.tn.node().id).classed(`er ${s}`,true).attr("x",0).attr("y",n).attr("width",d+a*2+r).attr("height",e.height+i*2);const p=parseFloat(c.attr("x"))+parseFloat(c.attr("width"));e.nn.attr("transform","translate("+(p+a)+","+o+")");const _=t.insert("rect","#"+e.nn.node().id).classed(`er ${s}`,true).attr("x",p).attr("y",n).attr("width",u+a*2+r).attr("height",e.height+i*2);let E=parseFloat(_.attr("x"))+parseFloat(_.attr("width"));if(l){e.kn.attr("transform","translate("+(E+a)+","+o+")");const c=t.insert("rect","#"+e.kn.node().id).classed(`er ${s}`,true).attr("x",E).attr("y",n).attr("width",y+a*2+r).attr("height",e.height+i*2);E=parseFloat(c.attr("x"))+parseFloat(c.attr("width"))}if(h){e.cn.attr("transform","translate("+(E+a)+","+o+")");t.insert("rect","#"+e.cn.node().id).classed(`er ${s}`,"true").attr("x",E).attr("y",n).attr("width",f+a*2+r).attr("height",e.height+i*2)}n+=e.height+i*2;s=s==="attributeBoxOdd"?"attributeBoxEven":"attributeBoxOdd"}))}else{g.height=Math.max(G.minEntityHeight,p);e.attr("transform","translate("+g.width/2+","+g.height/2+")")}return g};const X=function(t,e,r){const i=Object.keys(e);let a;i.forEach((function(i){const s=it(i,"entity");H.set(i,s);const o=t.append("g").attr("id",s);a=a===void 0?s:a;const c="text-"+s;const l=o.append("text").classed("er entityLabel",true).attr("id",c).attr("x",0).attr("y",0).style("dominant-baseline","middle").style("text-anchor","middle").style("font-family",(0,n.c)().fontFamily).style("font-size",G.fontSize+"px").text(e[i].alias??i);const{width:h,height:d}=Q(o,l,e[i].attributes);const u=o.insert("rect","#"+c).classed("er entityBox",true).attr("x",0).attr("y",0).attr("width",h).attr("height",d);const y=u.node().getBBox();r.setNode(s,{width:y.width,height:y.height,shape:"rect",id:s})}));return a};const q=function(t,e){e.nodes().forEach((function(r){if(r!==void 0&&e.node(r)!==void 0){t.select("#"+r).attr("transform","translate("+(e.node(r).x-e.node(r).width/2)+","+(e.node(r).y-e.node(r).height/2)+" )")}}))};const J=function(t){return(t.entityA+t.roleA+t.entityB).replace(/\s/g,"")};const V=function(t,e){t.forEach((function(t){e.setEdge(H.get(t.entityA),H.get(t.entityB),{relationship:t},J(t))}));return t};let tt=0;const et=function(t,e,r,i,s){tt++;const o=r.edge(H.get(e.entityA),H.get(e.entityB),J(e));const c=(0,a.jvg)().x((function(t){return t.x})).y((function(t){return t.y})).curve(a.$0Z);const l=t.insert("path","#"+i).classed("er relationshipLine",true).attr("d",c(o.points)).style("stroke",G.stroke).style("fill","none");if(e.relSpec.relType===s.db.Identification.NON_IDENTIFYING){l.attr("stroke-dasharray","8,8")}let h="";if(G.arrowMarkerAbsolute){h=window.location.protocol+"//"+window.location.host+window.location.pathname+window.location.search;h=h.replace(/\(/g,"\\(");h=h.replace(/\)/g,"\\)")}switch(e.relSpec.cardA){case s.db.Cardinality.ZERO_OR_ONE:l.attr("marker-end","url("+h+"#"+W.ERMarkers.ZERO_OR_ONE_END+")");break;case s.db.Cardinality.ZERO_OR_MORE:l.attr("marker-end","url("+h+"#"+W.ERMarkers.ZERO_OR_MORE_END+")");break;case s.db.Cardinality.ONE_OR_MORE:l.attr("marker-end","url("+h+"#"+W.ERMarkers.ONE_OR_MORE_END+")");break;case s.db.Cardinality.ONLY_ONE:l.attr("marker-end","url("+h+"#"+W.ERMarkers.ONLY_ONE_END+")");break;case s.db.Cardinality.MD_PARENT:l.attr("marker-end","url("+h+"#"+W.ERMarkers.MD_PARENT_END+")");break}switch(e.relSpec.cardB){case s.db.Cardinality.ZERO_OR_ONE:l.attr("marker-start","url("+h+"#"+W.ERMarkers.ZERO_OR_ONE_START+")");break;case s.db.Cardinality.ZERO_OR_MORE:l.attr("marker-start","url("+h+"#"+W.ERMarkers.ZERO_OR_MORE_START+")");break;case s.db.Cardinality.ONE_OR_MORE:l.attr("marker-start","url("+h+"#"+W.ERMarkers.ONE_OR_MORE_START+")");break;case s.db.Cardinality.ONLY_ONE:l.attr("marker-start","url("+h+"#"+W.ERMarkers.ONLY_ONE_START+")");break;case s.db.Cardinality.MD_PARENT:l.attr("marker-start","url("+h+"#"+W.ERMarkers.MD_PARENT_START+")");break}const d=l.node().getTotalLength();const u=l.node().getPointAtLength(d*.5);const y="rel"+tt;const f=t.append("text").classed("er relationshipLabel",true).attr("id",y).attr("x",u.x).attr("y",u.y).style("text-anchor","middle").style("dominant-baseline","middle").style("font-family",(0,n.c)().fontFamily).style("font-size",G.fontSize+"px").text(e.roleA);const p=f.node().getBBox();t.insert("rect","#"+y).classed("er relationshipLabelBox",true).attr("x",u.x-p.width/2).attr("y",u.y-p.height/2).attr("width",p.width).attr("height",p.height)};const rt=function(t,e,r,o){G=(0,n.c)().er;n.l.info("Drawing ER diagram");const c=(0,n.c)().securityLevel;let l;if(c==="sandbox"){l=(0,a.Ys)("#i"+e)}const h=c==="sandbox"?(0,a.Ys)(l.nodes()[0].contentDocument.body):(0,a.Ys)("body");const d=h.select(`[id='${e}']`);W.insertMarkers(d,G);let u;u=new i.k({multigraph:true,directed:true,compound:false}).setGraph({rankdir:G.layoutDirection,marginx:20,marginy:20,nodesep:100,edgesep:100,ranksep:100}).setDefaultEdgeLabel((function(){return{}}));const y=X(d,o.db.getEntities(),u);const f=V(o.db.getRelationships(),u);(0,s.bK)(u);q(d,u);f.forEach((function(t){et(d,t,u,y,o)}));const p=G.diagramPadding;n.u.insertTitle(d,"entityTitleText",G.titleTopMargin,o.db.getDiagramTitle());const _=d.node().getBBox();const E=_.width+p*2;const m=_.height+p*2;(0,n.i)(d,m,E,G.useMaxWidth);d.attr("viewBox",`${_.x-p} ${_.y-p} ${E} ${m}`)};const nt="28e9f9db-3c8d-5aa5-9faf-44286ae5937c";function it(t="",e=""){const r=t.replace(K,"");return`${at(e)}${at(r)}${T(t,nt)}`}function at(t=""){return t.length>0?`${t}-`:""}const st={setConf:j,draw:rt};const ot=t=>`\n  .entityBox {\n    fill: ${t.mainBkg};\n    stroke: ${t.nodeBorder};\n  }\n\n  .attributeBoxOdd {\n    fill: ${t.attributeBackgroundColorOdd};\n    stroke: ${t.nodeBorder};\n  }\n\n  .attributeBoxEven {\n    fill:  ${t.attributeBackgroundColorEven};\n    stroke: ${t.nodeBorder};\n  }\n\n  .relationshipLabelBox {\n    fill: ${t.tertiaryColor};\n    opacity: 0.7;\n    background-color: ${t.tertiaryColor};\n      rect {\n        opacity: 0.5;\n      }\n  }\n\n    .relationshipLine {\n      stroke: ${t.lineColor};\n    }\n\n  .entityTitleText {\n    text-anchor: middle;\n    font-size: 18px;\n    fill: ${t.textColor};\n  }    \n  #MD_PARENT_START {\n    fill: #f5f5f5 !important;\n    stroke: ${t.lineColor} !important;\n    stroke-width: 1;\n  }\n  #MD_PARENT_END {\n    fill: #f5f5f5 !important;\n    stroke: ${t.lineColor} !important;\n    stroke-width: 1;\n  }\n  \n`;const ct=ot;const lt={parser:w,db:F,renderer:st,styles:ct}}}]);