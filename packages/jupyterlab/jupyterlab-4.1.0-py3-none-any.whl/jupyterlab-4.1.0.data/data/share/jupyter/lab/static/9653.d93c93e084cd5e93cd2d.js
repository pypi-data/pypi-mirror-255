"use strict";(self["webpackChunk_jupyterlab_application_top"]=self["webpackChunk_jupyterlab_application_top"]||[]).push([[9653],{79653:(t,e,a)=>{a.r(e);a.d(e,{Tag:()=>s,classHighlighter:()=>I,getStyleTags:()=>b,highlightTree:()=>u,styleTags:()=>g,tagHighlighter:()=>p,tags:()=>E});var i=a(73265);var r=a.n(i);let o=0;class s{constructor(t,e,a){this.set=t;this.base=e;this.modified=a;this.id=o++}static define(t){if(t===null||t===void 0?void 0:t.base)throw new Error("Can not derive from a modified tag");let e=new s([],null,[]);e.set.push(e);if(t)for(let a of t.set)e.set.push(a);return e}static defineModifier(){let t=new l;return e=>{if(e.modified.indexOf(t)>-1)return e;return l.get(e.base||e,e.modified.concat(t).sort(((t,e)=>t.id-e.id)))}}}let n=0;class l{constructor(){this.instances=[];this.id=n++}static get(t,e){if(!e.length)return t;let a=e[0].instances.find((a=>a.base==t&&c(e,a.modified)));if(a)return a;let i=[],r=new s(i,t,e);for(let s of e)s.instances.push(r);let o=h(e);for(let s of t.set)if(!s.modified.length)for(let t of o)i.push(l.get(s,t));return r}}function c(t,e){return t.length==e.length&&t.every(((t,a)=>t==e[a]))}function h(t){let e=[[]];for(let a=0;a<t.length;a++){for(let i=0,r=e.length;i<r;i++){e.push(e[i].concat(t[a]))}}return e.sort(((t,e)=>e.length-t.length))}function g(t){let e=Object.create(null);for(let a in t){let i=t[a];if(!Array.isArray(i))i=[i];for(let t of a.split(" "))if(t){let a=[],r=2,o=t;for(let e=0;;){if(o=="..."&&e>0&&e+3==t.length){r=1;break}let i=/^"(?:[^"\\]|\\.)*?"|[^\/!]+/.exec(o);if(!i)throw new RangeError("Invalid path: "+t);a.push(i[0]=="*"?"":i[0][0]=='"'?JSON.parse(i[0]):i[0]);e+=i[0].length;if(e==t.length)break;let s=t[e++];if(e==t.length&&s=="!"){r=0;break}if(s!="/")throw new RangeError("Invalid path: "+t);o=t.slice(e)}let s=a.length-1,n=a[s];if(!n)throw new RangeError("Invalid path: "+t);let l=new d(i,r,s>0?a.slice(0,s):null);e[n]=l.sort(e[n])}}return f.add(e)}const f=new i.NodeProp;class d{constructor(t,e,a,i){this.tags=t;this.mode=e;this.context=a;this.next=i}get opaque(){return this.mode==0}get inherit(){return this.mode==1}sort(t){if(!t||t.depth<this.depth){this.next=t;return this}t.next=this.sort(t.next);return t}get depth(){return this.context?this.context.length:0}}d.empty=new d([],2,null);function p(t,e){let a=Object.create(null);for(let o of t){if(!Array.isArray(o.tag))a[o.tag.id]=o.class;else for(let t of o.tag)a[t.id]=o.class}let{scope:i,all:r=null}=e||{};return{style:t=>{let e=r;for(let i of t){for(let t of i.set){let i=a[t.id];if(i){e=e?e+" "+i:i;break}}}return e},scope:i}}function m(t,e){let a=null;for(let i of t){let t=i.style(e);if(t)a=a?a+" "+t:t}return a}function u(t,e,a,i=0,r=t.length){let o=new k(i,Array.isArray(e)?e:[e],a);o.highlightRange(t.cursor(),i,r,"",o.highlighters);o.flush(r)}class k{constructor(t,e,a){this.at=t;this.highlighters=e;this.span=a;this.class=""}startSpan(t,e){if(e!=this.class){this.flush(t);if(t>this.at)this.at=t;this.class=e}}flush(t){if(t>this.at&&this.class)this.span(this.at,t,this.class)}highlightRange(t,e,a,r,o){let{type:s,from:n,to:l}=t;if(n>=a||l<=e)return;if(s.isTop)o=this.highlighters.filter((t=>!t.scope||t.scope(s)));let c=r;let h=b(t)||d.empty;let g=m(o,h.tags);if(g){if(c)c+=" ";c+=g;if(h.mode==1)r+=(r?" ":"")+g}this.startSpan(t.from,c);if(h.opaque)return;let f=t.tree&&t.tree.prop(i.NodeProp.mounted);if(f&&f.overlay){let i=t.node.enter(f.overlay[0].from+n,1);let s=this.highlighters.filter((t=>!t.scope||t.scope(f.tree.type)));let h=t.firstChild();for(let g=0,d=n;;g++){let p=g<f.overlay.length?f.overlay[g]:null;let m=p?p.from+n:l;let u=Math.max(e,d),k=Math.min(a,m);if(u<k&&h){while(t.from<k){this.highlightRange(t,u,k,r,o);this.startSpan(Math.min(k,t.to),c);if(t.to>=m||!t.nextSibling())break}}if(!p||m>a)break;d=p.to+n;if(d>e){this.highlightRange(i.cursor(),Math.max(e,p.from+n),Math.min(a,d),r,s);this.startSpan(d,c)}}if(h)t.parent()}else if(t.firstChild()){do{if(t.to<=e)continue;if(t.from>=a)break;this.highlightRange(t,e,a,r,o);this.startSpan(Math.min(a,t.to),c)}while(t.nextSibling());t.parent()}}}function b(t){let e=t.type.prop(f);while(e&&e.context&&!t.matchContext(e.context))e=e.next;return e||null}const y=s.define;const N=y(),w=y(),v=y(w),x=y(w),M=y(),O=y(M),S=y(M),C=y(),R=y(C),A=y(),_=y(),T=y(),j=y(T),q=y();const E={comment:N,lineComment:y(N),blockComment:y(N),docComment:y(N),name:w,variableName:y(w),typeName:v,tagName:y(v),propertyName:x,attributeName:y(x),className:y(w),labelName:y(w),namespace:y(w),macroName:y(w),literal:M,string:O,docString:y(O),character:y(O),attributeValue:y(O),number:S,integer:y(S),float:y(S),bool:y(M),regexp:y(M),escape:y(M),color:y(M),url:y(M),keyword:A,self:y(A),null:y(A),atom:y(A),unit:y(A),modifier:y(A),operatorKeyword:y(A),controlKeyword:y(A),definitionKeyword:y(A),moduleKeyword:y(A),operator:_,derefOperator:y(_),arithmeticOperator:y(_),logicOperator:y(_),bitwiseOperator:y(_),compareOperator:y(_),updateOperator:y(_),definitionOperator:y(_),typeOperator:y(_),controlOperator:y(_),punctuation:T,separator:y(T),bracket:j,angleBracket:y(j),squareBracket:y(j),paren:y(j),brace:y(j),content:C,heading:R,heading1:y(R),heading2:y(R),heading3:y(R),heading4:y(R),heading5:y(R),heading6:y(R),contentSeparator:y(C),list:y(C),quote:y(C),emphasis:y(C),strong:y(C),link:y(C),monospace:y(C),strikethrough:y(C),inserted:y(),deleted:y(),changed:y(),invalid:y(),meta:q,documentMeta:y(q),annotation:y(q),processingInstruction:y(q),definition:s.defineModifier(),constant:s.defineModifier(),function:s.defineModifier(),standard:s.defineModifier(),local:s.defineModifier(),special:s.defineModifier()};const I=p([{tag:E.link,class:"tok-link"},{tag:E.heading,class:"tok-heading"},{tag:E.emphasis,class:"tok-emphasis"},{tag:E.strong,class:"tok-strong"},{tag:E.keyword,class:"tok-keyword"},{tag:E.atom,class:"tok-atom"},{tag:E.bool,class:"tok-bool"},{tag:E.url,class:"tok-url"},{tag:E.labelName,class:"tok-labelName"},{tag:E.inserted,class:"tok-inserted"},{tag:E.deleted,class:"tok-deleted"},{tag:E.literal,class:"tok-literal"},{tag:E.string,class:"tok-string"},{tag:E.number,class:"tok-number"},{tag:[E.regexp,E.escape,E.special(E.string)],class:"tok-string2"},{tag:E.variableName,class:"tok-variableName"},{tag:E.local(E.variableName),class:"tok-variableName tok-local"},{tag:E.definition(E.variableName),class:"tok-variableName tok-definition"},{tag:E.special(E.variableName),class:"tok-variableName2"},{tag:E.definition(E.propertyName),class:"tok-propertyName tok-definition"},{tag:E.typeName,class:"tok-typeName"},{tag:E.namespace,class:"tok-namespace"},{tag:E.className,class:"tok-className"},{tag:E.macroName,class:"tok-macroName"},{tag:E.propertyName,class:"tok-propertyName"},{tag:E.operator,class:"tok-operator"},{tag:E.comment,class:"tok-comment"},{tag:E.meta,class:"tok-meta"},{tag:E.invalid,class:"tok-invalid"},{tag:E.punctuation,class:"tok-punctuation"}])}}]);