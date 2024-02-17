import { c as Jn, a as Qn, g as er } from "./module-2c3384e6.js";
import { g as Kt } from "./index-fdcab7e8.js";
const Rt = /* @__PURE__ */ new Set(), tr = Jn({
  encode: ({ call: e }) => async (t, n) => {
    const r = await e("encode", { encoderId: t, timeslice: n });
    return Rt.delete(t), r;
  },
  instantiate: ({ call: e }) => async (t, n) => {
    const r = Qn(Rt), o = await e("instantiate", { encoderId: r, mimeType: t, sampleRate: n });
    return { encoderId: r, port: o };
  },
  register: ({ call: e }) => (t) => e("register", { port: t }, [t])
}), nr = (e) => {
  const t = new Worker(e);
  return tr(t);
}, rr = `(()=>{var e={775:function(e,t,r){!function(e,t,r,n){"use strict";var o=function(e,t){return void 0===t?e:t.reduce((function(e,t){if("capitalize"===t){var o=e.charAt(0).toUpperCase(),s=e.slice(1);return"".concat(o).concat(s)}return"dashify"===t?r(e):"prependIndefiniteArticle"===t?"".concat(n(e)," ").concat(e):e}),e)},s=function(e){var t=e.name+e.modifiers.map((function(e){return"\\\\.".concat(e,"\\\\(\\\\)")})).join("");return new RegExp("\\\\$\\\\{".concat(t,"}"),"g")},a=function(e,r){for(var n=/\\\${([^.}]+)((\\.[^(]+\\(\\))*)}/g,a=[],i=n.exec(e);null!==i;){var c={modifiers:[],name:i[1]};if(void 0!==i[3])for(var u=/\\.[^(]+\\(\\)/g,l=u.exec(i[2]);null!==l;)c.modifiers.push(l[0].slice(1,-2)),l=u.exec(i[2]);a.push(c),i=n.exec(e)}var d=a.reduce((function(e,n){return e.map((function(e){return"string"==typeof e?e.split(s(n)).reduce((function(e,s,a){return 0===a?[s]:n.name in r?[].concat(t(e),[o(r[n.name],n.modifiers),s]):[].concat(t(e),[function(e){return o(e[n.name],n.modifiers)},s])}),[]):[e]})).reduce((function(e,r){return[].concat(t(e),t(r))}),[])}),[e]);return function(e){return d.reduce((function(r,n){return[].concat(t(r),"string"==typeof n?[n]:[n(e)])}),[]).join("")}},i=function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=void 0===e.code?void 0:a(e.code,t),n=void 0===e.message?void 0:a(e.message,t);function o(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},o=arguments.length>1?arguments[1]:void 0,s=void 0===o&&(t instanceof Error||void 0!==t.code&&"Exception"===t.code.slice(-9))?{cause:t,missingParameters:{}}:{cause:o,missingParameters:t},a=s.cause,i=s.missingParameters,c=void 0===n?new Error:new Error(n(i));return null!==a&&(c.cause=a),void 0!==r&&(c.code=r(i)),void 0!==e.status&&(c.status=e.status),c}return o};e.compile=i}(t,r(106),r(881),r(507))},881:e=>{"use strict";e.exports=(e,t)=>{if("string"!=typeof e)throw new TypeError("expected a string");return e.trim().replace(/([a-z])([A-Z])/g,"$1-$2").replace(/\\W/g,(e=>/[À-ž]/.test(e)?e:"-")).replace(/^-+|-+$/g,"").replace(/-{2,}/g,(e=>t&&t.condense?"-":e)).toLowerCase()}},107:function(e,t){!function(e){"use strict";var t=function(e){return function(t){var r=e(t);return t.add(r),r}},r=function(e){return function(t,r){return e.set(t,r),r}},n=void 0===Number.MAX_SAFE_INTEGER?9007199254740991:Number.MAX_SAFE_INTEGER,o=536870912,s=2*o,a=function(e,t){return function(r){var a=t.get(r),i=void 0===a?r.size:a<s?a+1:0;if(!r.has(i))return e(r,i);if(r.size<o){for(;r.has(i);)i=Math.floor(Math.random()*s);return e(r,i)}if(r.size>n)throw new Error("Congratulations, you created a collection of unique numbers which uses all available integers!");for(;r.has(i);)i=Math.floor(Math.random()*n);return e(r,i)}},i=new WeakMap,c=r(i),u=a(c,i),l=t(u);e.addUniqueNumber=l,e.generateUniqueNumber=u}(t)},507:e=>{var t=function(e){var t,r,n=/\\w+/.exec(e);if(!n)return"an";var o=(r=n[0]).toLowerCase(),s=["honest","hour","hono"];for(t in s)if(0==o.indexOf(s[t]))return"an";if(1==o.length)return"aedhilmnorsx".indexOf(o)>=0?"an":"a";if(r.match(/(?!FJO|[HLMNS]Y.|RY[EO]|SQU|(F[LR]?|[HL]|MN?|N|RH?|S[CHKLMNPTVW]?|X(YL)?)[AEIOU])[FHLMNRSX][A-Z]/))return"an";var a=[/^e[uw]/,/^onc?e\\b/,/^uni([^nmd]|mo)/,/^u[bcfhjkqrst][aeiou]/];for(t=0;t<a.length;t++)if(o.match(a[t]))return"a";return r.match(/^U[NK][AIEO]/)?"a":r==r.toUpperCase()?"aedhilmnorsx".indexOf(o[0])>=0?"an":"a":"aeiou".indexOf(o[0])>=0||o.match(/^y(b[lor]|cl[ea]|fere|gg|p[ios]|rou|tt)/)?"an":"a"};void 0!==e.exports?e.exports=t:window.indefiniteArticle=t},768:e=>{e.exports=function(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n},e.exports.__esModule=!0,e.exports.default=e.exports},907:(e,t,r)=>{var n=r(768);e.exports=function(e){if(Array.isArray(e))return n(e)},e.exports.__esModule=!0,e.exports.default=e.exports},642:e=>{e.exports=function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)},e.exports.__esModule=!0,e.exports.default=e.exports},344:e=>{e.exports=function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")},e.exports.__esModule=!0,e.exports.default=e.exports},106:(e,t,r)=>{var n=r(907),o=r(642),s=r(906),a=r(344);e.exports=function(e){return n(e)||o(e)||s(e)||a()},e.exports.__esModule=!0,e.exports.default=e.exports},906:(e,t,r)=>{var n=r(768);e.exports=function(e,t){if(e){if("string"==typeof e)return n(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?n(e,t):void 0}},e.exports.__esModule=!0,e.exports.default=e.exports}},t={};function r(n){var o=t[n];if(void 0!==o)return o.exports;var s=t[n]={exports:{}};return e[n].call(s.exports,s,s.exports,r),s.exports}(()=>{"use strict";var e=r(775);const t=-32603,n=-32602,o=-32601,s=(0,e.compile)({message:'The requested method called "\${method}" is not supported.',status:o}),a=(0,e.compile)({message:'The handler of the method called "\${method}" returned no required result.',status:t}),i=(0,e.compile)({message:'The handler of the method called "\${method}" returned an unexpected result.',status:t}),c=(0,e.compile)({message:'The specified parameter called "portId" with the given value "\${portId}" does not identify a port connected to this worker.',status:n});var u=r(107);const l=new Map,d=(e,t,r)=>({...t,connect:r=>{let{port:n}=r;n.start();const o=e(n,t),s=(0,u.generateUniqueNumber)(l);return l.set(s,(()=>{o(),n.close(),l.delete(s)})),{result:s}},disconnect:e=>{let{portId:t}=e;const r=l.get(t);if(void 0===r)throw c({portId:t.toString()});return r(),{result:null}},isSupported:async()=>{if(await new Promise((e=>{const t=new ArrayBuffer(0),{port1:r,port2:n}=new MessageChannel;r.onmessage=t=>{let{data:r}=t;return e(null!==r)},n.postMessage(t,[t])}))){const e=r();return{result:e instanceof Promise?await e:e}}return{result:!1}}}),f=function(e,t){const r=d(f,t,arguments.length>2&&void 0!==arguments[2]?arguments[2]:()=>!0),n=((e,t)=>async r=>{let{data:{id:n,method:o,params:c}}=r;const u=t[o];try{if(void 0===u)throw s({method:o});const t=void 0===c?u():u(c);if(void 0===t)throw a({method:o});const r=t instanceof Promise?await t:t;if(null===n){if(void 0!==r.result)throw i({method:o})}else{if(void 0===r.result)throw i({method:o});const{result:t,transferables:s=[]}=r;e.postMessage({id:n,result:t},s)}}catch(t){const{message:r,status:o=-32603}=t;e.postMessage({error:{code:o,message:r},id:n})}})(e,r);return e.addEventListener("message",n),()=>e.removeEventListener("message",n)},p=e=>{e.onmessage=null,e.close()},m=new WeakMap,h=new WeakMap,g=(e=>{const t=(r=e,{...r,connect:e=>{let{call:t}=e;return async()=>{const{port1:e,port2:r}=new MessageChannel,n=await t("connect",{port:e},[e]);return m.set(r,n),r}},disconnect:e=>{let{call:t}=e;return async e=>{const r=m.get(e);if(void 0===r)throw new Error("The given port is not connected.");await t("disconnect",{portId:r})}},isSupported:e=>{let{call:t}=e;return()=>t("isSupported")}});var r;return e=>{const r=(e=>{if(h.has(e))return h.get(e);const t=new Map;return h.set(e,t),t})(e);e.addEventListener("message",(e=>{let{data:t}=e;const{id:n}=t;if(null!==n&&r.has(n)){const{reject:e,resolve:o}=r.get(n);r.delete(n),void 0===t.error?o(t.result):e(new Error(t.error.message))}})),(e=>"function"==typeof e.start)(e)&&e.start();const n=function(t){let n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,o=arguments.length>2&&void 0!==arguments[2]?arguments[2]:[];return new Promise(((s,a)=>{const i=(0,u.generateUniqueNumber)(r);r.set(i,{reject:a,resolve:s}),null===n?e.postMessage({id:i,method:t},o):e.postMessage({id:i,method:t,params:n},o)}))},o=function(t,r){let n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:[];e.postMessage({id:null,method:t,params:r},n)};let s={};for(const[e,r]of Object.entries(t))s={...s,[e]:r({call:n,notify:o})};return{...s}}})({characterize:e=>{let{call:t}=e;return()=>t("characterize")},encode:e=>{let{call:t}=e;return(e,r)=>t("encode",{recordingId:e,timeslice:r})},record:e=>{let{call:t}=e;return async(e,r,n)=>{await t("record",{recordingId:e,sampleRate:r,typedArrays:n},n.map((e=>{let{buffer:t}=e;return t})))}}}),v=async(e,t)=>{const r=g(t),n=await r.characterize(),o=n.toString();if(e.has(o))throw new Error("There is already an encoder stored which handles exactly the same mime types.");return e.set(o,[n,r]),n},w=new Map,x=(e=>t=>{const r=e.get(t);if(void 0===r)throw new Error("There was no instance of an encoder stored with the given id.");return r})(w),y=((e,t)=>r=>{const n=t(r);return e.delete(r),n})(w,x),M=new Map,b=((e,t)=>r=>{const[n,o,s,a]=t(r);return s?new Promise((t=>{o.onmessage=s=>{let{data:i}=s;0===i.length?(e(o),t(n.encode(r,null))):n.record(r,a,i)}})):n.encode(r,null)})(p,y),E=(e=>t=>{for(const[r,n]of Array.from(e.values()))if(r.test(t))return n;throw new Error("There is no encoder registered which could handle the given mimeType.")})(M),A=((e,t,r)=>(n,o,s)=>{if(t.has(n))throw new Error('There is already an encoder registered with an id called "'.concat(n,'".'));const a=r(o),{port1:i,port2:c}=new MessageChannel,u=[a,i,!0,s];return t.set(n,u),i.onmessage=t=>{let{data:r}=t;0===r.length?(e(i),u[2]=!1):a.record(n,s,r.map((e=>"number"==typeof e?new Float32Array(e):e)))},c})(p,w,E),I=(e=>(t,r)=>{const[n]=e(t);return n.encode(t,r)})(x);f(self,{encode:async e=>{let{encoderId:t,timeslice:r}=e;const n=null===r?await b(t):await I(t,r);return{result:n,transferables:n}},instantiate:e=>{let{encoderId:t,mimeType:r,sampleRate:n}=e;const o=A(t,r,n);return{result:o,transferables:[o]}},register:async e=>{let{port:t}=e;return{result:await v(M,t)}}})})()})();`, or = new Blob([rr], { type: "application/javascript; charset=utf-8" }), Jt = URL.createObjectURL(or), dt = nr(Jt), Se = dt.encode, Qt = dt.instantiate, sr = dt.register;
URL.revokeObjectURL(Jt);
const ir = (e) => (t, n) => {
  if (e === null)
    throw new Error("A native BlobEvent could not be created.");
  return new e(t, n);
}, ar = (e, t) => (n, r, o) => {
  const s = [];
  let i = r, c = 0;
  for (; c < n.byteLength; )
    if (i === null) {
      const a = t(n, c);
      if (a === null)
        break;
      const { length: u, type: d } = a;
      i = d, c += u;
    } else {
      const a = e(n, c, i, o);
      if (a === null)
        break;
      const { content: u, length: d } = a;
      i = null, c += d, u !== null && s.push(u);
    }
  return { contents: s, currentElementType: i, offset: c };
}, cr = (e, t) => class {
  constructor(r = null) {
    this._listeners = /* @__PURE__ */ new WeakMap(), this._nativeEventTarget = r === null ? e() : r;
  }
  addEventListener(r, o, s) {
    if (o !== null) {
      let i = this._listeners.get(o);
      i === void 0 && (i = t(this, o), typeof o == "function" && this._listeners.set(o, i)), this._nativeEventTarget.addEventListener(r, i, s);
    }
  }
  dispatchEvent(r) {
    return this._nativeEventTarget.dispatchEvent(r);
  }
  removeEventListener(r, o, s) {
    const i = o === null ? void 0 : this._listeners.get(o);
    this._nativeEventTarget.removeEventListener(r, i === void 0 ? null : i, s);
  }
}, ur = (e) => () => {
  if (e === null)
    throw new Error("A native EventTarget could not be created.");
  return e.document.createElement("p");
}, lr = (e = "") => {
  try {
    return new DOMException(e, "InvalidModificationError");
  } catch (t) {
    return t.code = 13, t.message = e, t.name = "InvalidModificationError", t;
  }
}, dr = () => {
  try {
    return new DOMException("", "InvalidStateError");
  } catch (e) {
    return e.code = 11, e.name = "InvalidStateError", e;
  }
}, fr = (e) => {
  if (e !== null && // Bug #14: Before v14.1 Safari did not support the BlobEvent.
  e.BlobEvent !== void 0 && e.MediaStream !== void 0 && /*
   * Bug #10: An early experimental implemenation in Safari v14 did not provide the isTypeSupported() function.
   *
   * Bug #17: Safari up to v14.1.2 throttled the processing on hidden tabs if there was no active audio output. This is not tested
   * here but should be covered by the following test, too.
   */
  (e.MediaRecorder === void 0 || e.MediaRecorder.isTypeSupported !== void 0)) {
    if (e.MediaRecorder === void 0)
      return Promise.resolve(!0);
    const t = e.document.createElement("canvas"), n = t.getContext("2d");
    if (n === null || typeof t.captureStream != "function")
      return Promise.resolve(!1);
    const r = t.captureStream();
    return Promise.all([
      /*
       * Bug #5: Up until v70 Firefox did emit a blob of type video/webm when asked to encode a MediaStream with a video track into an
       * audio codec.
       */
      new Promise((o) => {
        const s = "audio/webm";
        try {
          const i = new e.MediaRecorder(r, { mimeType: s });
          i.addEventListener("dataavailable", ({ data: c }) => o(c.type === s)), i.start(), setTimeout(() => i.stop(), 10);
        } catch (i) {
          o(i.name === "NotSupportedError");
        }
      }),
      /*
       * Bug #1 & #2: Up until v83 Firefox fired an error event with an UnknownError when adding or removing a track.
       *
       * Bug #3 & #4: Up until v112 Chrome dispatched an error event without any error.
       *
       * Bug #6: Up until v113 Chrome emitted a blob without any data when asked to encode a MediaStream with a video track as audio.
       * This is not directly tested here as it can only be tested by recording something for a short time. It got fixed at the same
       * time as #7 and #8.
       *
       * Bug #7 & #8: Up until v113 Chrome dispatched the dataavailable and stop events before it dispatched the error event.
       */
      new Promise((o) => {
        const s = new e.MediaRecorder(r);
        let i = !1, c = !1;
        s.addEventListener("dataavailable", () => i = !0), s.addEventListener("error", (a) => {
          o(!i && !c && "error" in a && a.error !== null && typeof a.error == "object" && "name" in a.error && a.error.name !== "UnknownError");
        }), s.addEventListener("stop", () => c = !0), s.start(), n.fillRect(0, 0, 1, 1), r.removeTrack(r.getVideoTracks()[0]);
      })
    ]).then((o) => o.every((s) => s));
  }
  return Promise.resolve(!1);
}, hr = (e, t, n, r, o, s, i) => class extends s {
  constructor(a, u = {}) {
    const { mimeType: d } = u;
    if (i !== null && // Bug #10: Safari does not yet implement the isTypeSupported() method.
    (d === void 0 || i.isTypeSupported !== void 0 && i.isTypeSupported(d))) {
      const l = e(i, a, u);
      super(l), this._internalMediaRecorder = l;
    } else if (d !== void 0 && o.some((l) => l.test(d)))
      super(), i !== null && i.isTypeSupported !== void 0 && i.isTypeSupported("audio/webm;codecs=pcm") ? this._internalMediaRecorder = r(this, i, a, d) : this._internalMediaRecorder = n(this, a, d);
    else
      throw i !== null && e(i, a, u), t();
    this._ondataavailable = null, this._onerror = null, this._onpause = null, this._onresume = null, this._onstart = null, this._onstop = null;
  }
  get mimeType() {
    return this._internalMediaRecorder.mimeType;
  }
  get ondataavailable() {
    return this._ondataavailable === null ? this._ondataavailable : this._ondataavailable[0];
  }
  set ondataavailable(a) {
    if (this._ondataavailable !== null && this.removeEventListener("dataavailable", this._ondataavailable[1]), typeof a == "function") {
      const u = a.bind(this);
      this.addEventListener("dataavailable", u), this._ondataavailable = [a, u];
    } else
      this._ondataavailable = null;
  }
  get onerror() {
    return this._onerror === null ? this._onerror : this._onerror[0];
  }
  set onerror(a) {
    if (this._onerror !== null && this.removeEventListener("error", this._onerror[1]), typeof a == "function") {
      const u = a.bind(this);
      this.addEventListener("error", u), this._onerror = [a, u];
    } else
      this._onerror = null;
  }
  get onpause() {
    return this._onpause === null ? this._onpause : this._onpause[0];
  }
  set onpause(a) {
    if (this._onpause !== null && this.removeEventListener("pause", this._onpause[1]), typeof a == "function") {
      const u = a.bind(this);
      this.addEventListener("pause", u), this._onpause = [a, u];
    } else
      this._onpause = null;
  }
  get onresume() {
    return this._onresume === null ? this._onresume : this._onresume[0];
  }
  set onresume(a) {
    if (this._onresume !== null && this.removeEventListener("resume", this._onresume[1]), typeof a == "function") {
      const u = a.bind(this);
      this.addEventListener("resume", u), this._onresume = [a, u];
    } else
      this._onresume = null;
  }
  get onstart() {
    return this._onstart === null ? this._onstart : this._onstart[0];
  }
  set onstart(a) {
    if (this._onstart !== null && this.removeEventListener("start", this._onstart[1]), typeof a == "function") {
      const u = a.bind(this);
      this.addEventListener("start", u), this._onstart = [a, u];
    } else
      this._onstart = null;
  }
  get onstop() {
    return this._onstop === null ? this._onstop : this._onstop[0];
  }
  set onstop(a) {
    if (this._onstop !== null && this.removeEventListener("stop", this._onstop[1]), typeof a == "function") {
      const u = a.bind(this);
      this.addEventListener("stop", u), this._onstop = [a, u];
    } else
      this._onstop = null;
  }
  get state() {
    return this._internalMediaRecorder.state;
  }
  pause() {
    return this._internalMediaRecorder.pause();
  }
  resume() {
    return this._internalMediaRecorder.resume();
  }
  start(a) {
    return this._internalMediaRecorder.start(a);
  }
  stop() {
    return this._internalMediaRecorder.stop();
  }
  static isTypeSupported(a) {
    return i !== null && // Bug #10: Safari does not yet implement the isTypeSupported() method.
    i.isTypeSupported !== void 0 && i.isTypeSupported(a) || o.some((u) => u.test(a));
  }
}, pr = (e) => e !== null && e.BlobEvent !== void 0 ? e.BlobEvent : null, mr = (e) => e === null || e.MediaRecorder === void 0 ? null : e.MediaRecorder, gr = (e) => (t, n, r) => {
  const o = /* @__PURE__ */ new Map(), s = /* @__PURE__ */ new WeakMap(), i = /* @__PURE__ */ new WeakMap(), c = [], a = new t(n, r), u = /* @__PURE__ */ new WeakMap();
  return a.addEventListener("stop", ({ isTrusted: d }) => {
    d && setTimeout(() => c.shift());
  }), a.addEventListener = ((d) => (l, g, w) => {
    let p = g;
    if (typeof g == "function")
      if (l === "dataavailable") {
        const f = [];
        p = (m) => {
          const [[h, b] = [!1, !1]] = c;
          h && !b ? f.push(m) : g.call(a, m);
        }, o.set(g, f), s.set(g, p);
      } else
        l === "error" ? (p = (f) => {
          f instanceof ErrorEvent ? g.call(a, f) : g.call(a, new ErrorEvent("error", { error: f.error }));
        }, i.set(g, p)) : l === "stop" && (p = (f) => {
          for (const [m, h] of o.entries())
            if (h.length > 0) {
              const [b] = h;
              h.length > 1 && Object.defineProperty(b, "data", {
                value: new Blob(h.map(({ data: _ }) => _), { type: b.data.type })
              }), h.length = 0, m.call(a, b);
            }
          g.call(a, f);
        }, u.set(g, p));
    return d.call(a, l, p, w);
  })(a.addEventListener), a.removeEventListener = ((d) => (l, g, w) => {
    let p = g;
    if (typeof g == "function") {
      if (l === "dataavailable") {
        o.delete(g);
        const f = s.get(g);
        f !== void 0 && (p = f);
      } else if (l === "error") {
        const f = i.get(g);
        f !== void 0 && (p = f);
      } else if (l === "stop") {
        const f = u.get(g);
        f !== void 0 && (p = f);
      }
    }
    return d.call(a, l, p, w);
  })(a.removeEventListener), a.start = ((d) => (l) => {
    if (r.mimeType !== void 0 && r.mimeType.startsWith("audio/") && n.getVideoTracks().length > 0)
      throw e();
    return a.state === "inactive" && c.push([l !== void 0, !0]), l === void 0 ? d.call(a) : d.call(a, l);
  })(a.start), a.stop = ((d) => () => {
    a.state !== "inactive" && (c[0][1] = !1), d.call(a);
  })(a.stop), a;
}, et = () => {
  try {
    return new DOMException("", "NotSupportedError");
  } catch (e) {
    return e.code = 9, e.name = "NotSupportedError", e;
  }
}, wr = (e) => (t, n, r, o = 2) => {
  const s = e(t, n);
  if (s === null)
    return s;
  const { length: i, value: c } = s;
  if (r === "master")
    return { content: null, length: i };
  if (n + i + c > t.byteLength)
    return null;
  if (r === "binary") {
    const a = (c / Float32Array.BYTES_PER_ELEMENT - 1) / o, u = Array.from({ length: o }, () => new Float32Array(a));
    for (let d = 0; d < a; d += 1) {
      const l = d * o + 1;
      for (let g = 0; g < o; g += 1)
        u[g][d] = t.getFloat32(n + i + (l + g) * Float32Array.BYTES_PER_ELEMENT, !0);
    }
    return { content: u, length: i + c };
  }
  return { content: null, length: i + c };
}, vr = (e) => (t, n) => {
  const r = e(t, n);
  if (r === null)
    return r;
  const { length: o, value: s } = r;
  return s === 35 ? { length: o, type: "binary" } : s === 46 || s === 97 || s === 88713574 || s === 106212971 || s === 139690087 || s === 172351395 || s === 256095861 ? { length: o, type: "master" } : { length: o, type: "unknown" };
}, _r = (e) => (t, n) => {
  const r = e(t, n);
  if (r === null)
    return r;
  const o = n + Math.floor((r - 1) / 8);
  if (o + r > t.byteLength)
    return null;
  let i = t.getUint8(o) & (1 << 8 - r % 8) - 1;
  for (let c = 1; c < r; c += 1)
    i = (i << 8) + t.getUint8(o + c);
  return { length: r, value: i };
}, It = Symbol.observable || "@@observable";
function yr(e) {
  return Symbol.observable || (typeof e == "function" && e.prototype && e.prototype[Symbol.observable] ? (e.prototype[It] = e.prototype[Symbol.observable], delete e.prototype[Symbol.observable]) : (e[It] = e[Symbol.observable], delete e[Symbol.observable])), e;
}
const Ne = () => {
}, St = (e) => {
  throw e;
};
function Er(e) {
  return e ? e.next && e.error && e.complete ? e : {
    complete: (e.complete ?? Ne).bind(e),
    error: (e.error ?? St).bind(e),
    next: (e.next ?? Ne).bind(e)
  } : {
    complete: Ne,
    error: St,
    next: Ne
  };
}
const Ar = (e) => (t, n, r) => e((o) => {
  const s = (i) => o.next(i);
  return t.addEventListener(n, s, r), () => t.removeEventListener(n, s, r);
}), br = (e, t) => {
  const n = () => {
  }, r = (o) => typeof o[0] == "function";
  return (o) => {
    const s = (...i) => {
      const c = o(r(i) ? t({ next: i[0] }) : t(...i));
      return c !== void 0 ? c : n;
    };
    return s[Symbol.observable] = () => ({
      subscribe: (...i) => ({ unsubscribe: s(...i) })
    }), e(s);
  };
}, Cr = br(yr, Er), en = Ar(Cr);
/*!
 * dashify <https://github.com/jonschlinkert/dashify>
 *
 * Copyright (c) 2015-2017, Jon Schlinkert.
 * Released under the MIT License.
 */
var Tr = (e, t) => {
  if (typeof e != "string")
    throw new TypeError("expected a string");
  return e.trim().replace(/([a-z])([A-Z])/g, "$1-$2").replace(/\W/g, (n) => /[À-ž]/.test(n) ? n : "-").replace(/^-+|-+$/g, "").replace(/-{2,}/g, (n) => t && t.condense ? "-" : n).toLowerCase();
};
const Mr = /* @__PURE__ */ Kt(Tr);
var tn = { exports: {} };
(function(e) {
  var t = function(n) {
    var r, o, s = /\w+/.exec(n);
    if (s)
      o = s[0];
    else
      return "an";
    var i = o.toLowerCase(), c = ["honest", "hour", "hono"];
    for (r in c)
      if (i.indexOf(c[r]) == 0)
        return "an";
    if (i.length == 1)
      return "aedhilmnorsx".indexOf(i) >= 0 ? "an" : "a";
    if (o.match(/(?!FJO|[HLMNS]Y.|RY[EO]|SQU|(F[LR]?|[HL]|MN?|N|RH?|S[CHKLMNPTVW]?|X(YL)?)[AEIOU])[FHLMNRSX][A-Z]/))
      return "an";
    var a = [/^e[uw]/, /^onc?e\b/, /^uni([^nmd]|mo)/, /^u[bcfhjkqrst][aeiou]/];
    for (r = 0; r < a.length; r++)
      if (i.match(a[r]))
        return "a";
    return o.match(/^U[NK][AIEO]/) ? "a" : o == o.toUpperCase() ? "aedhilmnorsx".indexOf(i[0]) >= 0 ? "an" : "a" : "aeiou".indexOf(i[0]) >= 0 || i.match(/^y(b[lor]|cl[ea]|fere|gg|p[ios]|rou|tt)/) ? "an" : "a";
  };
  e.exports = t;
})(tn);
var Nr = tn.exports;
const Or = /* @__PURE__ */ Kt(Nr), kt = (e, t) => t === void 0 ? e : t.reduce((n, r) => {
  if (r === "capitalize") {
    const o = n.charAt(0).toUpperCase(), s = n.slice(1);
    return `${o}${s}`;
  }
  return r === "dashify" ? Mr(n) : r === "prependIndefiniteArticle" ? `${Or(n)} ${n}` : n;
}, e), Rr = (e) => {
  const t = e.name + e.modifiers.map((n) => `\\.${n}\\(\\)`).join("");
  return new RegExp(`\\$\\{${t}}`, "g");
}, Lt = (e, t) => {
  const n = /\${([^.}]+)((\.[^(]+\(\))*)}/g, r = [];
  let o = n.exec(e);
  for (; o !== null; ) {
    const i = {
      modifiers: [],
      name: o[1]
    };
    if (o[3] !== void 0) {
      const c = /\.[^(]+\(\)/g;
      let a = c.exec(o[2]);
      for (; a !== null; )
        i.modifiers.push(a[0].slice(1, -2)), a = c.exec(o[2]);
    }
    r.push(i), o = n.exec(e);
  }
  const s = r.reduce((i, c) => i.map((a) => typeof a == "string" ? a.split(Rr(c)).reduce((u, d, l) => l === 0 ? [d] : c.name in t ? [...u, kt(t[c.name], c.modifiers), d] : [...u, (g) => kt(g[c.name], c.modifiers), d], []) : [a]).reduce((a, u) => [...a, ...u], []), [e]);
  return (i) => s.reduce((c, a) => typeof a == "string" ? [...c, a] : [...c, a(i)], []).join("");
}, We = (e, t = {}) => {
  const n = e.code === void 0 ? void 0 : Lt(e.code, t), r = e.message === void 0 ? void 0 : Lt(e.message, t);
  function o(s = {}, i) {
    const c = i === void 0 && (s instanceof Error || s.code !== void 0 && s.code.slice(-9) === "Exception"), { cause: a, missingParameters: u } = c ? {
      cause: s,
      missingParameters: {}
    } : {
      cause: i,
      missingParameters: s
    }, d = r === void 0 ? new Error() : new Error(r(u));
    return a !== null && (d.cause = a), n !== void 0 && (d.code = n(u)), e.status !== void 0 && (d.status = e.status), d;
  }
  return o;
}, Ve = { INTERNAL_ERROR: -32603, INVALID_PARAMS: -32602, METHOD_NOT_FOUND: -32601 };
We({
  message: 'The requested method called "${method}" is not supported.',
  status: Ve.METHOD_NOT_FOUND
});
We({
  message: 'The handler of the method called "${method}" returned no required result.',
  status: Ve.INTERNAL_ERROR
});
We({
  message: 'The handler of the method called "${method}" returned an unexpected result.',
  status: Ve.INTERNAL_ERROR
});
We({
  message: 'The specified parameter called "portId" with the given value "${portId}" does not identify a port connected to this worker.',
  status: Ve.INVALID_PARAMS
});
const Ir = (e, t, n) => async (r) => {
  const o = new e([n], { type: "application/javascript; charset=utf-8" }), s = t.createObjectURL(o);
  try {
    await r(s);
  } finally {
    t.revokeObjectURL(s);
  }
}, Sr = (e) => ({ data: t }) => {
  const { id: n } = t;
  if (n !== null) {
    const r = e.get(n);
    if (r !== void 0) {
      const { reject: o, resolve: s } = r;
      e.delete(n), t.error === void 0 ? s(t.result) : o(new Error(t.error.message));
    }
  }
}, kr = (e) => (t, n) => (r, o = []) => new Promise((s, i) => {
  const c = e(t);
  t.set(c, { reject: i, resolve: s }), n.postMessage({ id: c, ...r }, o);
}), Lr = (e, t, n, r) => (o, s, i = {}) => {
  const c = new o(s, "recorder-audio-worklet-processor", {
    ...i,
    channelCountMode: "explicit",
    numberOfInputs: 1,
    numberOfOutputs: 0
  }), a = /* @__PURE__ */ new Map(), u = t(a, c.port), d = n(c.port, "message")(e(a));
  c.port.start();
  let l = "inactive";
  return Object.defineProperties(c, {
    pause: {
      get() {
        return async () => (r(["recording"], l), l = "paused", u({
          method: "pause"
        }));
      }
    },
    port: {
      get() {
        throw new Error("The port of a RecorderAudioWorkletNode can't be accessed.");
      }
    },
    record: {
      get() {
        return async (g) => (r(["inactive"], l), l = "recording", u({
          method: "record",
          params: { encoderPort: g }
        }, [g]));
      }
    },
    resume: {
      get() {
        return async () => (r(["paused"], l), l = "recording", u({
          method: "resume"
        }));
      }
    },
    stop: {
      get() {
        return async () => {
          r(["paused", "recording"], l), l = "stopped";
          try {
            await u({ method: "stop" });
          } finally {
            d();
          }
        };
      }
    }
  }), c;
}, xr = (e, t) => {
  if (!e.includes(t))
    throw new Error(`Expected the state to be ${e.map((n) => `"${n}"`).join(" or ")} but it was "${t}".`);
}, Pr = '(()=>{"use strict";class e extends AudioWorkletProcessor{constructor(){super(),this._encoderPort=null,this._numberOfChannels=0,this._state="inactive",this.port.onmessage=e=>{let{data:t}=e;"pause"===t.method?"active"===this._state||"recording"===this._state?(this._state="paused",this._sendAcknowledgement(t.id)):this._sendUnexpectedStateError(t.id):"record"===t.method?"inactive"===this._state?(this._encoderPort=t.params.encoderPort,this._state="active",this._sendAcknowledgement(t.id)):this._sendUnexpectedStateError(t.id):"resume"===t.method?"paused"===this._state?(this._state="active",this._sendAcknowledgement(t.id)):this._sendUnexpectedStateError(t.id):"stop"===t.method?"active"!==this._state&&"paused"!==this._state&&"recording"!==this._state||null===this._encoderPort?this._sendUnexpectedStateError(t.id):(this._stop(this._encoderPort),this._sendAcknowledgement(t.id)):"number"==typeof t.id&&this.port.postMessage({error:{code:-32601,message:"The requested method is not supported."},id:t.id})}}process(e){let[t]=e;if("inactive"===this._state||"paused"===this._state)return!0;if("active"===this._state){if(void 0===t)throw new Error("No channelData was received for the first input.");if(0===t.length)return!0;this._state="recording"}if("recording"===this._state&&null!==this._encoderPort){if(void 0===t)throw new Error("No channelData was received for the first input.");return 0===t.length?this._encoderPort.postMessage(Array.from({length:this._numberOfChannels},(()=>128))):(this._encoderPort.postMessage(t,t.map((e=>{let{buffer:t}=e;return t}))),this._numberOfChannels=t.length),!0}return!1}_sendAcknowledgement(e){this.port.postMessage({id:e,result:null})}_sendUnexpectedStateError(e){this.port.postMessage({error:{code:-32603,message:"The internal state does not allow to process the given message."},id:e})}_stop(e){e.postMessage([]),e.close(),this._encoderPort=null,this._state="stopped"}}e.parameterDescriptors=[],registerProcessor("recorder-audio-worklet-processor",e)})();', Ur = Ir(Blob, URL, Pr), Br = Lr(Sr, kr(er), en, xr), xt = (e, t, n) => ({ endTime: t, insertTime: n, type: "exponentialRampToValue", value: e }), Pt = (e, t, n) => ({ endTime: t, insertTime: n, type: "linearRampToValue", value: e }), tt = (e, t) => ({ startTime: t, type: "setValue", value: e }), nn = (e, t, n) => ({ duration: n, startTime: t, type: "setValueCurve", values: e }), rn = (e, t, { startTime: n, target: r, timeConstant: o }) => r + (t - r) * Math.exp((n - e) / o), me = (e) => e.type === "exponentialRampToValue", ke = (e) => e.type === "linearRampToValue", re = (e) => me(e) || ke(e), ft = (e) => e.type === "setValue", Q = (e) => e.type === "setValueCurve", Le = (e, t, n, r) => {
  const o = e[t];
  return o === void 0 ? r : re(o) || ft(o) ? o.value : Q(o) ? o.values[o.values.length - 1] : rn(n, Le(e, t - 1, o.startTime, r), o);
}, Ut = (e, t, n, r, o) => n === void 0 ? [r.insertTime, o] : re(n) ? [n.endTime, n.value] : ft(n) ? [n.startTime, n.value] : Q(n) ? [
  n.startTime + n.duration,
  n.values[n.values.length - 1]
] : [
  n.startTime,
  Le(e, t - 1, n.startTime, o)
], nt = (e) => e.type === "cancelAndHold", rt = (e) => e.type === "cancelScheduledValues", ne = (e) => nt(e) || rt(e) ? e.cancelTime : me(e) || ke(e) ? e.endTime : e.startTime, Bt = (e, t, n, { endTime: r, value: o }) => n === o ? o : 0 < n && 0 < o || n < 0 && o < 0 ? n * (o / n) ** ((e - t) / (r - t)) : 0, Dt = (e, t, n, { endTime: r, value: o }) => n + (e - t) / (r - t) * (o - n), Dr = (e, t) => {
  const n = Math.floor(t), r = Math.ceil(t);
  return n === r ? e[n] : (1 - (t - n)) * e[n] + (1 - (r - t)) * e[r];
}, Wr = (e, { duration: t, startTime: n, values: r }) => {
  const o = (e - n) / t * (r.length - 1);
  return Dr(r, o);
}, Oe = (e) => e.type === "setTarget";
class Vr {
  constructor(t) {
    this._automationEvents = [], this._currenTime = 0, this._defaultValue = t;
  }
  [Symbol.iterator]() {
    return this._automationEvents[Symbol.iterator]();
  }
  add(t) {
    const n = ne(t);
    if (nt(t) || rt(t)) {
      const r = this._automationEvents.findIndex((s) => rt(t) && Q(s) ? s.startTime + s.duration >= n : ne(s) >= n), o = this._automationEvents[r];
      if (r !== -1 && (this._automationEvents = this._automationEvents.slice(0, r)), nt(t)) {
        const s = this._automationEvents[this._automationEvents.length - 1];
        if (o !== void 0 && re(o)) {
          if (s !== void 0 && Oe(s))
            throw new Error("The internal list is malformed.");
          const i = s === void 0 ? o.insertTime : Q(s) ? s.startTime + s.duration : ne(s), c = s === void 0 ? this._defaultValue : Q(s) ? s.values[s.values.length - 1] : s.value, a = me(o) ? Bt(n, i, c, o) : Dt(n, i, c, o), u = me(o) ? xt(a, n, this._currenTime) : Pt(a, n, this._currenTime);
          this._automationEvents.push(u);
        }
        if (s !== void 0 && Oe(s) && this._automationEvents.push(tt(this.getValue(n), n)), s !== void 0 && Q(s) && s.startTime + s.duration > n) {
          const i = n - s.startTime, c = (s.values.length - 1) / s.duration, a = Math.max(2, 1 + Math.ceil(i * c)), u = i / (a - 1) * c, d = s.values.slice(0, a);
          if (u < 1)
            for (let l = 1; l < a; l += 1) {
              const g = u * l % 1;
              d[l] = s.values[l - 1] * (1 - g) + s.values[l] * g;
            }
          this._automationEvents[this._automationEvents.length - 1] = nn(d, s.startTime, i);
        }
      }
    } else {
      const r = this._automationEvents.findIndex((i) => ne(i) > n), o = r === -1 ? this._automationEvents[this._automationEvents.length - 1] : this._automationEvents[r - 1];
      if (o !== void 0 && Q(o) && ne(o) + o.duration > n)
        return !1;
      const s = me(t) ? xt(t.value, t.endTime, this._currenTime) : ke(t) ? Pt(t.value, n, this._currenTime) : t;
      if (r === -1)
        this._automationEvents.push(s);
      else {
        if (Q(t) && n + t.duration > ne(this._automationEvents[r]))
          return !1;
        this._automationEvents.splice(r, 0, s);
      }
    }
    return !0;
  }
  flush(t) {
    const n = this._automationEvents.findIndex((r) => ne(r) > t);
    if (n > 1) {
      const r = this._automationEvents.slice(n - 1), o = r[0];
      Oe(o) && r.unshift(tt(Le(this._automationEvents, n - 2, o.startTime, this._defaultValue), o.startTime)), this._automationEvents = r;
    }
  }
  getValue(t) {
    if (this._automationEvents.length === 0)
      return this._defaultValue;
    const n = this._automationEvents.findIndex((i) => ne(i) > t), r = this._automationEvents[n], o = (n === -1 ? this._automationEvents.length : n) - 1, s = this._automationEvents[o];
    if (s !== void 0 && Oe(s) && (r === void 0 || !re(r) || r.insertTime > t))
      return rn(t, Le(this._automationEvents, o - 1, s.startTime, this._defaultValue), s);
    if (s !== void 0 && ft(s) && (r === void 0 || !re(r)))
      return s.value;
    if (s !== void 0 && Q(s) && (r === void 0 || !re(r) || s.startTime + s.duration > t))
      return t < s.startTime + s.duration ? Wr(t, s) : s.values[s.values.length - 1];
    if (s !== void 0 && re(s) && (r === void 0 || !re(r)))
      return s.value;
    if (r !== void 0 && me(r)) {
      const [i, c] = Ut(this._automationEvents, o, s, r, this._defaultValue);
      return Bt(t, i, c, r);
    }
    if (r !== void 0 && ke(r)) {
      const [i, c] = Ut(this._automationEvents, o, s, r, this._defaultValue);
      return Dt(t, i, c, r);
    }
    return this._defaultValue;
  }
}
const Fr = (e) => ({ cancelTime: e, type: "cancelAndHold" }), jr = (e) => ({ cancelTime: e, type: "cancelScheduledValues" }), $r = (e, t) => ({ endTime: t, type: "exponentialRampToValue", value: e }), Gr = (e, t) => ({ endTime: t, type: "linearRampToValue", value: e }), qr = (e, t, n) => ({ startTime: t, target: e, timeConstant: n, type: "setTarget" }), zr = () => new DOMException("", "AbortError"), Hr = (e) => (t, n, [r, o, s], i) => {
  e(t[o], [n, r, s], (c) => c[0] === n && c[1] === r, i);
}, Yr = (e) => (t, n, r) => {
  const o = [];
  for (let s = 0; s < r.numberOfInputs; s += 1)
    o.push(/* @__PURE__ */ new Set());
  e.set(t, {
    activeInputs: o,
    outputs: /* @__PURE__ */ new Set(),
    passiveInputs: /* @__PURE__ */ new WeakMap(),
    renderer: n
  });
}, Xr = (e) => (t, n) => {
  e.set(t, { activeInputs: /* @__PURE__ */ new Set(), passiveInputs: /* @__PURE__ */ new WeakMap(), renderer: n });
}, ge = /* @__PURE__ */ new WeakSet(), on = /* @__PURE__ */ new WeakMap(), sn = /* @__PURE__ */ new WeakMap(), an = /* @__PURE__ */ new WeakMap(), cn = /* @__PURE__ */ new WeakMap(), un = /* @__PURE__ */ new WeakMap(), ln = /* @__PURE__ */ new WeakMap(), ot = /* @__PURE__ */ new WeakMap(), st = /* @__PURE__ */ new WeakMap(), it = /* @__PURE__ */ new WeakMap(), dn = {
  construct() {
    return dn;
  }
}, Zr = (e) => {
  try {
    const t = new Proxy(e, dn);
    new t();
  } catch {
    return !1;
  }
  return !0;
}, Wt = /^import(?:(?:[\s]+[\w]+|(?:[\s]+[\w]+[\s]*,)?[\s]*\{[\s]*[\w]+(?:[\s]+as[\s]+[\w]+)?(?:[\s]*,[\s]*[\w]+(?:[\s]+as[\s]+[\w]+)?)*[\s]*}|(?:[\s]+[\w]+[\s]*,)?[\s]*\*[\s]+as[\s]+[\w]+)[\s]+from)?(?:[\s]*)("([^"\\]|\\.)+"|'([^'\\]|\\.)+')(?:[\s]*);?/, Vt = (e, t) => {
  const n = [];
  let r = e.replace(/^[\s]+/, ""), o = r.match(Wt);
  for (; o !== null; ) {
    const s = o[1].slice(1, -1), i = o[0].replace(/([\s]+)?;?$/, "").replace(s, new URL(s, t).toString());
    n.push(i), r = r.slice(o[0].length).replace(/^[\s]+/, ""), o = r.match(Wt);
  }
  return [n.join(";"), r];
}, Ft = (e) => {
  if (e !== void 0 && !Array.isArray(e))
    throw new TypeError("The parameterDescriptors property of given value for processorCtor is not an array.");
}, jt = (e) => {
  if (!Zr(e))
    throw new TypeError("The given value for processorCtor should be a constructor.");
  if (e.prototype === null || typeof e.prototype != "object")
    throw new TypeError("The given value for processorCtor should have a prototype.");
}, Kr = (e, t, n, r, o, s, i, c, a, u, d, l, g) => {
  let w = 0;
  return (p, f, m = { credentials: "omit" }) => {
    const h = d.get(p);
    if (h !== void 0 && h.has(f))
      return Promise.resolve();
    const b = u.get(p);
    if (b !== void 0) {
      const E = b.get(f);
      if (E !== void 0)
        return E;
    }
    const _ = s(p), T = _.audioWorklet === void 0 ? o(f).then(([E, A]) => {
      const [y, v] = Vt(E, A), M = `${y};((a,b)=>{(a[b]=a[b]||[]).push((AudioWorkletProcessor,global,registerProcessor,sampleRate,self,window)=>{${v}
})})(window,'_AWGS')`;
      return n(M);
    }).then(() => {
      const E = g._AWGS.pop();
      if (E === void 0)
        throw new SyntaxError();
      r(_.currentTime, _.sampleRate, () => E(class {
      }, void 0, (A, y) => {
        if (A.trim() === "")
          throw t();
        const v = st.get(_);
        if (v !== void 0) {
          if (v.has(A))
            throw t();
          jt(y), Ft(y.parameterDescriptors), v.set(A, y);
        } else
          jt(y), Ft(y.parameterDescriptors), st.set(_, /* @__PURE__ */ new Map([[A, y]]));
      }, _.sampleRate, void 0, void 0));
    }) : Promise.all([
      o(f),
      Promise.resolve(e(l, l))
    ]).then(([[E, A], y]) => {
      const v = w + 1;
      w = v;
      const [M, S] = Vt(E, A), P = `${M};((AudioWorkletProcessor,registerProcessor)=>{${S}
})(${y ? "AudioWorkletProcessor" : "class extends AudioWorkletProcessor {__b=new WeakSet();constructor(){super();(p=>p.postMessage=(q=>(m,t)=>q.call(p,m,t?t.filter(u=>!this.__b.has(u)):t))(p.postMessage))(this.port)}}"},(n,p)=>registerProcessor(n,class extends p{${y ? "" : "__c = (a) => a.forEach(e=>this.__b.add(e.buffer));"}process(i,o,p){${y ? "" : "i.forEach(this.__c);o.forEach(this.__c);this.__c(Object.values(p));"}return super.process(i.map(j=>j.some(k=>k.length===0)?[]:j),o,p)}}));registerProcessor('__sac${v}',class extends AudioWorkletProcessor{process(){return !1}})`, B = new Blob([P], { type: "application/javascript; charset=utf-8" }), I = URL.createObjectURL(B);
      return _.audioWorklet.addModule(I, m).then(() => {
        if (c(_))
          return _;
        const U = i(_);
        return U.audioWorklet.addModule(I, m).then(() => U);
      }).then((U) => {
        if (a === null)
          throw new SyntaxError();
        try {
          new a(U, `__sac${v}`);
        } catch {
          throw new SyntaxError();
        }
      }).finally(() => URL.revokeObjectURL(I));
    });
    return b === void 0 ? u.set(p, /* @__PURE__ */ new Map([[f, T]])) : b.set(f, T), T.then(() => {
      const E = d.get(p);
      E === void 0 ? d.set(p, /* @__PURE__ */ new Set([f])) : E.add(f);
    }).finally(() => {
      const E = u.get(p);
      E !== void 0 && E.delete(f);
    }), T;
  };
}, K = (e, t) => {
  const n = e.get(t);
  if (n === void 0)
    throw new Error("A value with the given key could not be found.");
  return n;
}, Fe = (e, t) => {
  const n = Array.from(e).filter(t);
  if (n.length > 1)
    throw Error("More than one element was found.");
  if (n.length === 0)
    throw Error("No element was found.");
  const [r] = n;
  return e.delete(r), r;
}, fn = (e, t, n, r) => {
  const o = K(e, t), s = Fe(o, (i) => i[0] === n && i[1] === r);
  return o.size === 0 && e.delete(t), s;
}, Ae = (e) => K(ln, e), xe = (e) => {
  if (ge.has(e))
    throw new Error("The AudioNode is already stored.");
  ge.add(e), Ae(e).forEach((t) => t(!0));
}, hn = (e) => "port" in e, ht = (e) => {
  if (!ge.has(e))
    throw new Error("The AudioNode is not stored.");
  ge.delete(e), Ae(e).forEach((t) => t(!1));
}, at = (e, t) => {
  !hn(e) && t.every((n) => n.size === 0) && ht(e);
}, Jr = (e, t, n, r, o, s, i, c, a, u, d, l, g) => {
  const w = /* @__PURE__ */ new WeakMap();
  return (p, f, m, h, b) => {
    const { activeInputs: _, passiveInputs: T } = s(f), { outputs: E } = s(p), A = c(p), y = (v) => {
      const M = a(f), S = a(p);
      if (v) {
        const N = fn(T, p, m, h);
        e(_, p, N, !1), !b && !l(p) && n(S, M, m, h), g(f) && xe(f);
      } else {
        const N = r(_, p, m, h);
        t(T, h, N, !1), !b && !l(p) && o(S, M, m, h);
        const L = i(f);
        if (L === 0)
          d(f) && at(f, _);
        else {
          const x = w.get(f);
          x !== void 0 && clearTimeout(x), w.set(f, setTimeout(() => {
            d(f) && at(f, _);
          }, L * 1e3));
        }
      }
    };
    return u(E, [f, m, h], (v) => v[0] === f && v[1] === m && v[2] === h, !0) ? (A.add(y), d(p) ? e(_, p, [m, h, y], !0) : t(T, h, [p, m, y], !0), !0) : !1;
  };
}, Qr = (e) => (t, n, [r, o, s], i) => {
  const c = t.get(r);
  c === void 0 ? t.set(r, /* @__PURE__ */ new Set([[o, n, s]])) : e(c, [o, n, s], (a) => a[0] === o && a[1] === n, i);
}, eo = (e) => (t, n) => {
  const r = e(t, {
    channelCount: 1,
    channelCountMode: "explicit",
    channelInterpretation: "discrete",
    gain: 0
  });
  n.connect(r).connect(t.destination);
  const o = () => {
    n.removeEventListener("ended", o), n.disconnect(r), r.disconnect();
  };
  n.addEventListener("ended", o);
}, to = (e) => (t, n) => {
  e(t).add(n);
}, pn = (e, t) => e.context === t, $t = (e) => {
  try {
    e.copyToChannel(new Float32Array(1), 0, -1);
  } catch {
    return !1;
  }
  return !0;
}, ue = () => new DOMException("", "IndexSizeError"), no = (e) => {
  e.getChannelData = ((t) => (n) => {
    try {
      return t.call(e, n);
    } catch (r) {
      throw r.code === 12 ? ue() : r;
    }
  })(e.getChannelData);
}, ro = {
  numberOfChannels: 1
}, oo = (e, t, n, r, o, s, i, c) => {
  let a = null;
  return class mn {
    constructor(d) {
      if (o === null)
        throw new Error("Missing the native OfflineAudioContext constructor.");
      const { length: l, numberOfChannels: g, sampleRate: w } = { ...ro, ...d };
      a === null && (a = new o(1, 1, 44100));
      const p = r !== null && t(s, s) ? new r({ length: l, numberOfChannels: g, sampleRate: w }) : a.createBuffer(g, l, w);
      if (p.numberOfChannels === 0)
        throw n();
      return typeof p.copyFromChannel != "function" ? (i(p), no(p)) : t($t, () => $t(p)) || c(p), e.add(p), p;
    }
    static [Symbol.hasInstance](d) {
      return d !== null && typeof d == "object" && Object.getPrototypeOf(d) === mn.prototype || e.has(d);
    }
  };
}, je = -34028234663852886e22, pt = -je, ie = (e) => ge.has(e), so = {
  buffer: null,
  channelCount: 2,
  channelCountMode: "max",
  channelInterpretation: "speakers",
  // Bug #149: Safari does not yet support the detune AudioParam.
  loop: !1,
  loopEnd: 0,
  loopStart: 0,
  playbackRate: 1
}, io = (e, t, n, r, o, s, i, c) => class extends e {
  constructor(u, d) {
    const l = s(u), g = { ...so, ...d }, w = o(l, g), p = i(l), f = p ? t() : null;
    super(u, !1, w, f), this._audioBufferSourceNodeRenderer = f, this._isBufferNullified = !1, this._isBufferSet = g.buffer !== null, this._nativeAudioBufferSourceNode = w, this._onended = null, this._playbackRate = n(this, p, w.playbackRate, pt, je);
  }
  get buffer() {
    return this._isBufferNullified ? null : this._nativeAudioBufferSourceNode.buffer;
  }
  set buffer(u) {
    if (this._nativeAudioBufferSourceNode.buffer = u, u !== null) {
      if (this._isBufferSet)
        throw r();
      this._isBufferSet = !0;
    }
  }
  get loop() {
    return this._nativeAudioBufferSourceNode.loop;
  }
  set loop(u) {
    this._nativeAudioBufferSourceNode.loop = u;
  }
  get loopEnd() {
    return this._nativeAudioBufferSourceNode.loopEnd;
  }
  set loopEnd(u) {
    this._nativeAudioBufferSourceNode.loopEnd = u;
  }
  get loopStart() {
    return this._nativeAudioBufferSourceNode.loopStart;
  }
  set loopStart(u) {
    this._nativeAudioBufferSourceNode.loopStart = u;
  }
  get onended() {
    return this._onended;
  }
  set onended(u) {
    const d = typeof u == "function" ? c(this, u) : null;
    this._nativeAudioBufferSourceNode.onended = d;
    const l = this._nativeAudioBufferSourceNode.onended;
    this._onended = l !== null && l === d ? u : l;
  }
  get playbackRate() {
    return this._playbackRate;
  }
  start(u = 0, d = 0, l) {
    if (this._nativeAudioBufferSourceNode.start(u, d, l), this._audioBufferSourceNodeRenderer !== null && (this._audioBufferSourceNodeRenderer.start = l === void 0 ? [u, d] : [u, d, l]), this.context.state !== "closed") {
      xe(this);
      const g = () => {
        this._nativeAudioBufferSourceNode.removeEventListener("ended", g), ie(this) && ht(this);
      };
      this._nativeAudioBufferSourceNode.addEventListener("ended", g);
    }
  }
  stop(u = 0) {
    this._nativeAudioBufferSourceNode.stop(u), this._audioBufferSourceNodeRenderer !== null && (this._audioBufferSourceNodeRenderer.stop = u);
  }
}, ao = (e, t, n, r, o) => () => {
  const s = /* @__PURE__ */ new WeakMap();
  let i = null, c = null;
  const a = async (u, d) => {
    let l = n(u);
    const g = pn(l, d);
    if (!g) {
      const w = {
        buffer: l.buffer,
        channelCount: l.channelCount,
        channelCountMode: l.channelCountMode,
        channelInterpretation: l.channelInterpretation,
        // Bug #149: Safari does not yet support the detune AudioParam.
        loop: l.loop,
        loopEnd: l.loopEnd,
        loopStart: l.loopStart,
        playbackRate: l.playbackRate.value
      };
      l = t(d, w), i !== null && l.start(...i), c !== null && l.stop(c);
    }
    return s.set(d, l), g ? await e(d, u.playbackRate, l.playbackRate) : await r(d, u.playbackRate, l.playbackRate), await o(u, d, l), l;
  };
  return {
    set start(u) {
      i = u;
    },
    set stop(u) {
      c = u;
    },
    render(u, d) {
      const l = s.get(d);
      return l !== void 0 ? Promise.resolve(l) : a(u, d);
    }
  };
}, co = (e) => "playbackRate" in e, uo = (e) => "frequency" in e && "gain" in e, lo = (e) => "offset" in e, fo = (e) => !("frequency" in e) && "gain" in e, ho = (e) => "detune" in e && "frequency" in e, po = (e) => "pan" in e, z = (e) => K(on, e), be = (e) => K(an, e), ct = (e, t) => {
  const { activeInputs: n } = z(e);
  n.forEach((o) => o.forEach(([s]) => {
    t.includes(e) || ct(s, [...t, e]);
  }));
  const r = co(e) ? [
    // Bug #149: Safari does not yet support the detune AudioParam.
    e.playbackRate
  ] : hn(e) ? Array.from(e.parameters.values()) : uo(e) ? [e.Q, e.detune, e.frequency, e.gain] : lo(e) ? [e.offset] : fo(e) ? [e.gain] : ho(e) ? [e.detune, e.frequency] : po(e) ? [e.pan] : [];
  for (const o of r) {
    const s = be(o);
    s !== void 0 && s.activeInputs.forEach(([i]) => ct(i, t));
  }
  ie(e) && ht(e);
}, mo = (e) => {
  ct(e.destination, []);
}, go = (e) => e === void 0 || typeof e == "number" || typeof e == "string" && (e === "balanced" || e === "interactive" || e === "playback"), wo = (e, t, n, r, o, s, i, c) => class extends e {
  constructor(u, d) {
    const l = s(u), g = i(l), w = o(l, d, g), p = g ? t(c) : null;
    super(u, !1, w, p), this._isNodeOfNativeOfflineAudioContext = g, this._nativeAudioDestinationNode = w;
  }
  get channelCount() {
    return this._nativeAudioDestinationNode.channelCount;
  }
  set channelCount(u) {
    if (this._isNodeOfNativeOfflineAudioContext)
      throw r();
    if (u > this._nativeAudioDestinationNode.maxChannelCount)
      throw n();
    this._nativeAudioDestinationNode.channelCount = u;
  }
  get channelCountMode() {
    return this._nativeAudioDestinationNode.channelCountMode;
  }
  set channelCountMode(u) {
    if (this._isNodeOfNativeOfflineAudioContext)
      throw r();
    this._nativeAudioDestinationNode.channelCountMode = u;
  }
  get maxChannelCount() {
    return this._nativeAudioDestinationNode.maxChannelCount;
  }
}, vo = (e) => {
  const t = /* @__PURE__ */ new WeakMap(), n = async (r, o) => {
    const s = o.destination;
    return t.set(o, s), await e(r, o, s), s;
  };
  return {
    render(r, o) {
      const s = t.get(o);
      return s !== void 0 ? Promise.resolve(s) : n(r, o);
    }
  };
}, _o = (e, t, n, r, o, s, i, c) => (a, u) => {
  const d = u.listener, l = () => {
    const E = new Float32Array(1), A = t(u, {
      channelCount: 1,
      channelCountMode: "explicit",
      channelInterpretation: "speakers",
      numberOfInputs: 9
    }), y = i(u);
    let v = !1, M = [0, 0, -1, 0, 1, 0], S = [0, 0, 0];
    const N = () => {
      if (v)
        return;
      v = !0;
      const B = r(u, 256, 9, 0);
      B.onaudioprocess = ({ inputBuffer: I }) => {
        const U = [
          s(I, E, 0),
          s(I, E, 1),
          s(I, E, 2),
          s(I, E, 3),
          s(I, E, 4),
          s(I, E, 5)
        ];
        U.some((O, k) => O !== M[k]) && (d.setOrientation(...U), M = U);
        const W = [
          s(I, E, 6),
          s(I, E, 7),
          s(I, E, 8)
        ];
        W.some((O, k) => O !== S[k]) && (d.setPosition(...W), S = W);
      }, A.connect(B);
    }, L = (B) => (I) => {
      I !== M[B] && (M[B] = I, d.setOrientation(...M));
    }, x = (B) => (I) => {
      I !== S[B] && (S[B] = I, d.setPosition(...S));
    }, P = (B, I, U) => {
      const W = n(u, {
        channelCount: 1,
        channelCountMode: "explicit",
        channelInterpretation: "discrete",
        offset: I
      });
      W.connect(A, 0, B), W.start(), Object.defineProperty(W.offset, "defaultValue", {
        get() {
          return I;
        }
      });
      const O = e({ context: a }, y, W.offset, pt, je);
      return c(O, "value", (k) => () => k.call(O), (k) => (V) => {
        try {
          k.call(O, V);
        } catch (G) {
          if (G.code !== 9)
            throw G;
        }
        N(), y && U(V);
      }), O.cancelAndHoldAtTime = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.cancelAndHoldAtTime), O.cancelScheduledValues = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.cancelScheduledValues), O.exponentialRampToValueAtTime = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.exponentialRampToValueAtTime), O.linearRampToValueAtTime = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.linearRampToValueAtTime), O.setTargetAtTime = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.setTargetAtTime), O.setValueAtTime = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.setValueAtTime), O.setValueCurveAtTime = ((k) => y ? () => {
        throw o();
      } : (...V) => {
        const G = k.apply(O, V);
        return N(), G;
      })(O.setValueCurveAtTime), O;
    };
    return {
      forwardX: P(0, 0, L(0)),
      forwardY: P(1, 0, L(1)),
      forwardZ: P(2, -1, L(2)),
      positionX: P(6, 0, x(0)),
      positionY: P(7, 0, x(1)),
      positionZ: P(8, 0, x(2)),
      upX: P(3, 0, L(3)),
      upY: P(4, 1, L(4)),
      upZ: P(5, 0, L(5))
    };
  }, { forwardX: g, forwardY: w, forwardZ: p, positionX: f, positionY: m, positionZ: h, upX: b, upY: _, upZ: T } = d.forwardX === void 0 ? l() : d;
  return {
    get forwardX() {
      return g;
    },
    get forwardY() {
      return w;
    },
    get forwardZ() {
      return p;
    },
    get positionX() {
      return f;
    },
    get positionY() {
      return m;
    },
    get positionZ() {
      return h;
    },
    get upX() {
      return b;
    },
    get upY() {
      return _;
    },
    get upZ() {
      return T;
    }
  };
}, Pe = (e) => "context" in e, Ce = (e) => Pe(e[0]), le = (e, t, n, r) => {
  for (const o of e)
    if (n(o)) {
      if (r)
        return !1;
      throw Error("The set contains at least one similar element.");
    }
  return e.add(t), !0;
}, Gt = (e, t, [n, r], o) => {
  le(e, [t, n, r], (s) => s[0] === t && s[1] === n, o);
}, qt = (e, [t, n, r], o) => {
  const s = e.get(t);
  s === void 0 ? e.set(t, /* @__PURE__ */ new Set([[n, r]])) : le(s, [n, r], (i) => i[0] === n, o);
}, gn = (e) => "inputs" in e, ut = (e, t, n, r) => {
  if (gn(t)) {
    const o = t.inputs[r];
    return e.connect(o, n, 0), [o, n, 0];
  }
  return e.connect(t, n, r), [t, n, r];
}, wn = (e, t, n) => {
  for (const r of e)
    if (r[0] === t && r[1] === n)
      return e.delete(r), r;
  return null;
}, yo = (e, t, n) => Fe(e, (r) => r[0] === t && r[1] === n), vn = (e, t) => {
  if (!Ae(e).delete(t))
    throw new Error("Missing the expected event listener.");
}, _n = (e, t, n) => {
  const r = K(e, t), o = Fe(r, (s) => s[0] === n);
  return r.size === 0 && e.delete(t), o;
}, lt = (e, t, n, r) => {
  gn(t) ? e.disconnect(t.inputs[r], n, 0) : e.disconnect(t, n, r);
}, X = (e) => K(sn, e), ye = (e) => K(cn, e), ae = (e) => ot.has(e), Ie = (e) => !ge.has(e), zt = (e, t) => new Promise((n) => {
  if (t !== null)
    n(!0);
  else {
    const r = e.createScriptProcessor(256, 1, 1), o = e.createGain(), s = e.createBuffer(1, 2, 44100), i = s.getChannelData(0);
    i[0] = 1, i[1] = 1;
    const c = e.createBufferSource();
    c.buffer = s, c.loop = !0, c.connect(r).connect(e.destination), c.connect(o), c.disconnect(o), r.onaudioprocess = (a) => {
      const u = a.inputBuffer.getChannelData(0);
      Array.prototype.some.call(u, (d) => d === 1) ? n(!0) : n(!1), c.stop(), r.onaudioprocess = null, c.disconnect(r), r.disconnect(e.destination);
    }, c.start();
  }
}), Je = (e, t) => {
  const n = /* @__PURE__ */ new Map();
  for (const r of e)
    for (const o of r) {
      const s = n.get(o);
      n.set(o, s === void 0 ? 1 : s + 1);
    }
  n.forEach((r, o) => t(o, r));
}, Ue = (e) => "context" in e, Eo = (e) => {
  const t = /* @__PURE__ */ new Map();
  e.connect = ((n) => (r, o = 0, s = 0) => {
    const i = Ue(r) ? n(r, o, s) : n(r, o), c = t.get(r);
    return c === void 0 ? t.set(r, [{ input: s, output: o }]) : c.every((a) => a.input !== s || a.output !== o) && c.push({ input: s, output: o }), i;
  })(e.connect.bind(e)), e.disconnect = ((n) => (r, o, s) => {
    if (n.apply(e), r === void 0)
      t.clear();
    else if (typeof r == "number")
      for (const [i, c] of t) {
        const a = c.filter((u) => u.output !== r);
        a.length === 0 ? t.delete(i) : t.set(i, a);
      }
    else if (t.has(r))
      if (o === void 0)
        t.delete(r);
      else {
        const i = t.get(r);
        if (i !== void 0) {
          const c = i.filter((a) => a.output !== o && (a.input !== s || s === void 0));
          c.length === 0 ? t.delete(r) : t.set(r, c);
        }
      }
    for (const [i, c] of t)
      c.forEach((a) => {
        Ue(i) ? e.connect(i, a.output, a.input) : e.connect(i, a.output);
      });
  })(e.disconnect);
}, Ao = (e, t, n, r) => {
  const { activeInputs: o, passiveInputs: s } = be(t), { outputs: i } = z(e), c = Ae(e), a = (u) => {
    const d = X(e), l = ye(t);
    if (u) {
      const g = _n(s, e, n);
      Gt(o, e, g, !1), !r && !ae(e) && d.connect(l, n);
    } else {
      const g = yo(o, e, n);
      qt(s, g, !1), !r && !ae(e) && d.disconnect(l, n);
    }
  };
  return le(i, [t, n], (u) => u[0] === t && u[1] === n, !0) ? (c.add(a), ie(e) ? Gt(o, e, [n, a], !0) : qt(s, [e, n, a], !0), !0) : !1;
}, bo = (e, t, n, r) => {
  const { activeInputs: o, passiveInputs: s } = z(t), i = wn(o[r], e, n);
  return i === null ? [fn(s, e, n, r)[2], !1] : [i[2], !0];
}, Co = (e, t, n) => {
  const { activeInputs: r, passiveInputs: o } = be(t), s = wn(r, e, n);
  return s === null ? [_n(o, e, n)[1], !1] : [s[2], !0];
}, mt = (e, t, n, r, o) => {
  const [s, i] = bo(e, n, r, o);
  if (s !== null && (vn(e, s), i && !t && !ae(e) && lt(X(e), X(n), r, o)), ie(n)) {
    const { activeInputs: c } = z(n);
    at(n, c);
  }
}, gt = (e, t, n, r) => {
  const [o, s] = Co(e, n, r);
  o !== null && (vn(e, o), s && !t && !ae(e) && X(e).disconnect(ye(n), r));
}, To = (e, t) => {
  const n = z(e), r = [];
  for (const o of n.outputs)
    Ce(o) ? mt(e, t, ...o) : gt(e, t, ...o), r.push(o[0]);
  return n.outputs.clear(), r;
}, Mo = (e, t, n) => {
  const r = z(e), o = [];
  for (const s of r.outputs)
    s[1] === n && (Ce(s) ? mt(e, t, ...s) : gt(e, t, ...s), o.push(s[0]), r.outputs.delete(s));
  return o;
}, No = (e, t, n, r, o) => {
  const s = z(e);
  return Array.from(s.outputs).filter((i) => i[0] === n && (r === void 0 || i[1] === r) && (o === void 0 || i[2] === o)).map((i) => (Ce(i) ? mt(e, t, ...i) : gt(e, t, ...i), s.outputs.delete(i), i[0]));
}, Oo = (e, t, n, r, o, s, i, c, a, u, d, l, g, w, p, f) => class extends u {
  constructor(h, b, _, T) {
    super(_), this._context = h, this._nativeAudioNode = _;
    const E = d(h);
    l(E) && n(zt, () => zt(E, f)) !== !0 && Eo(_), sn.set(this, _), ln.set(this, /* @__PURE__ */ new Set()), h.state !== "closed" && b && xe(this), e(this, T, _);
  }
  get channelCount() {
    return this._nativeAudioNode.channelCount;
  }
  set channelCount(h) {
    this._nativeAudioNode.channelCount = h;
  }
  get channelCountMode() {
    return this._nativeAudioNode.channelCountMode;
  }
  set channelCountMode(h) {
    this._nativeAudioNode.channelCountMode = h;
  }
  get channelInterpretation() {
    return this._nativeAudioNode.channelInterpretation;
  }
  set channelInterpretation(h) {
    this._nativeAudioNode.channelInterpretation = h;
  }
  get context() {
    return this._context;
  }
  get numberOfInputs() {
    return this._nativeAudioNode.numberOfInputs;
  }
  get numberOfOutputs() {
    return this._nativeAudioNode.numberOfOutputs;
  }
  // tslint:disable-next-line:invalid-void
  connect(h, b = 0, _ = 0) {
    if (b < 0 || b >= this._nativeAudioNode.numberOfOutputs)
      throw o();
    const T = d(this._context), E = p(T);
    if (g(h) || w(h))
      throw s();
    if (Pe(h)) {
      const v = X(h);
      try {
        const S = ut(this._nativeAudioNode, v, b, _), N = Ie(this);
        (E || N) && this._nativeAudioNode.disconnect(...S), this.context.state !== "closed" && !N && Ie(h) && xe(h);
      } catch (S) {
        throw S.code === 12 ? s() : S;
      }
      if (t(this, h, b, _, E)) {
        const S = a([this], h);
        Je(S, r(E));
      }
      return h;
    }
    const A = ye(h);
    if (A.name === "playbackRate" && A.maxValue === 1024)
      throw i();
    try {
      this._nativeAudioNode.connect(A, b), (E || Ie(this)) && this._nativeAudioNode.disconnect(A, b);
    } catch (v) {
      throw v.code === 12 ? s() : v;
    }
    if (Ao(this, h, b, E)) {
      const v = a([this], h);
      Je(v, r(E));
    }
  }
  disconnect(h, b, _) {
    let T;
    const E = d(this._context), A = p(E);
    if (h === void 0)
      T = To(this, A);
    else if (typeof h == "number") {
      if (h < 0 || h >= this.numberOfOutputs)
        throw o();
      T = Mo(this, A, h);
    } else {
      if (b !== void 0 && (b < 0 || b >= this.numberOfOutputs) || Pe(h) && _ !== void 0 && (_ < 0 || _ >= h.numberOfInputs))
        throw o();
      if (T = No(this, A, h, b, _), T.length === 0)
        throw s();
    }
    for (const y of T) {
      const v = a([this], y);
      Je(v, c);
    }
  }
}, Ro = (e, t, n, r, o, s, i, c, a, u, d, l, g) => (w, p, f, m = null, h = null) => {
  const b = f.value, _ = new Vr(b), T = p ? r(_) : null, E = {
    get defaultValue() {
      return b;
    },
    get maxValue() {
      return m === null ? f.maxValue : m;
    },
    get minValue() {
      return h === null ? f.minValue : h;
    },
    get value() {
      return f.value;
    },
    set value(A) {
      f.value = A, E.setValueAtTime(A, w.context.currentTime);
    },
    cancelAndHoldAtTime(A) {
      if (typeof f.cancelAndHoldAtTime == "function")
        T === null && _.flush(w.context.currentTime), _.add(o(A)), f.cancelAndHoldAtTime(A);
      else {
        const y = Array.from(_).pop();
        T === null && _.flush(w.context.currentTime), _.add(o(A));
        const v = Array.from(_).pop();
        f.cancelScheduledValues(A), y !== v && v !== void 0 && (v.type === "exponentialRampToValue" ? f.exponentialRampToValueAtTime(v.value, v.endTime) : v.type === "linearRampToValue" ? f.linearRampToValueAtTime(v.value, v.endTime) : v.type === "setValue" ? f.setValueAtTime(v.value, v.startTime) : v.type === "setValueCurve" && f.setValueCurveAtTime(v.values, v.startTime, v.duration));
      }
      return E;
    },
    cancelScheduledValues(A) {
      return T === null && _.flush(w.context.currentTime), _.add(s(A)), f.cancelScheduledValues(A), E;
    },
    exponentialRampToValueAtTime(A, y) {
      if (A === 0)
        throw new RangeError();
      if (!Number.isFinite(y) || y < 0)
        throw new RangeError();
      const v = w.context.currentTime;
      return T === null && _.flush(v), Array.from(_).length === 0 && (_.add(u(b, v)), f.setValueAtTime(b, v)), _.add(i(A, y)), f.exponentialRampToValueAtTime(A, y), E;
    },
    linearRampToValueAtTime(A, y) {
      const v = w.context.currentTime;
      return T === null && _.flush(v), Array.from(_).length === 0 && (_.add(u(b, v)), f.setValueAtTime(b, v)), _.add(c(A, y)), f.linearRampToValueAtTime(A, y), E;
    },
    setTargetAtTime(A, y, v) {
      return T === null && _.flush(w.context.currentTime), _.add(a(A, y, v)), f.setTargetAtTime(A, y, v), E;
    },
    setValueAtTime(A, y) {
      return T === null && _.flush(w.context.currentTime), _.add(u(A, y)), f.setValueAtTime(A, y), E;
    },
    setValueCurveAtTime(A, y, v) {
      const M = A instanceof Float32Array ? A : new Float32Array(A);
      if (l !== null && l.name === "webkitAudioContext") {
        const S = y + v, N = w.context.sampleRate, L = Math.ceil(y * N), x = Math.floor(S * N), P = x - L, B = new Float32Array(P);
        for (let U = 0; U < P; U += 1) {
          const W = (M.length - 1) / v * ((L + U) / N - y), O = Math.floor(W), k = Math.ceil(W);
          B[U] = O === k ? M[O] : (1 - (W - O)) * M[O] + (1 - (k - W)) * M[k];
        }
        T === null && _.flush(w.context.currentTime), _.add(d(B, y, v)), f.setValueCurveAtTime(B, y, v);
        const I = x / N;
        I < S && g(E, B[B.length - 1], I), g(E, M[M.length - 1], S);
      } else
        T === null && _.flush(w.context.currentTime), _.add(d(M, y, v)), f.setValueCurveAtTime(M, y, v);
      return E;
    }
  };
  return n.set(E, f), t.set(E, w), e(E, T), E;
}, Io = (e) => ({
  replay(t) {
    for (const n of e)
      if (n.type === "exponentialRampToValue") {
        const { endTime: r, value: o } = n;
        t.exponentialRampToValueAtTime(o, r);
      } else if (n.type === "linearRampToValue") {
        const { endTime: r, value: o } = n;
        t.linearRampToValueAtTime(o, r);
      } else if (n.type === "setTarget") {
        const { startTime: r, target: o, timeConstant: s } = n;
        t.setTargetAtTime(o, r, s);
      } else if (n.type === "setValue") {
        const { startTime: r, value: o } = n;
        t.setValueAtTime(o, r);
      } else if (n.type === "setValueCurve") {
        const { duration: r, startTime: o, values: s } = n;
        t.setValueCurveAtTime(s, o, r);
      } else
        throw new Error("Can't apply an unknown automation.");
  }
});
class yn {
  constructor(t) {
    this._map = new Map(t);
  }
  get size() {
    return this._map.size;
  }
  entries() {
    return this._map.entries();
  }
  forEach(t, n = null) {
    return this._map.forEach((r, o) => t.call(n, r, o, this));
  }
  get(t) {
    return this._map.get(t);
  }
  has(t) {
    return this._map.has(t);
  }
  keys() {
    return this._map.keys();
  }
  values() {
    return this._map.values();
  }
}
const So = {
  channelCount: 2,
  // Bug #61: The channelCountMode should be 'max' according to the spec but is set to 'explicit' to achieve consistent behavior.
  channelCountMode: "explicit",
  channelInterpretation: "speakers",
  numberOfInputs: 1,
  numberOfOutputs: 1,
  parameterData: {},
  processorOptions: {}
}, ko = (e, t, n, r, o, s, i, c, a, u, d, l, g, w) => class extends t {
  constructor(f, m, h) {
    var b;
    const _ = c(f), T = a(_), E = d({ ...So, ...h });
    g(E);
    const A = st.get(_), y = A == null ? void 0 : A.get(m), v = T || _.state !== "closed" ? _ : (b = i(_)) !== null && b !== void 0 ? b : _, M = o(v, T ? null : f.baseLatency, u, m, y, E), S = T ? r(m, E, y) : null;
    super(f, !0, M, S);
    const N = [];
    M.parameters.forEach((x, P) => {
      const B = n(this, T, x);
      N.push([P, B]);
    }), this._nativeAudioWorkletNode = M, this._onprocessorerror = null, this._parameters = new yn(N), T && e(_, this);
    const { activeInputs: L } = s(this);
    l(M, L);
  }
  get onprocessorerror() {
    return this._onprocessorerror;
  }
  set onprocessorerror(f) {
    const m = typeof f == "function" ? w(this, f) : null;
    this._nativeAudioWorkletNode.onprocessorerror = m;
    const h = this._nativeAudioWorkletNode.onprocessorerror;
    this._onprocessorerror = h !== null && h === m ? f : h;
  }
  get parameters() {
    return this._parameters === null ? this._nativeAudioWorkletNode.parameters : this._parameters;
  }
  get port() {
    return this._nativeAudioWorkletNode.port;
  }
};
function Be(e, t, n, r, o) {
  if (typeof e.copyFromChannel == "function")
    t[n].byteLength === 0 && (t[n] = new Float32Array(128)), e.copyFromChannel(t[n], r, o);
  else {
    const s = e.getChannelData(r);
    if (t[n].byteLength === 0)
      t[n] = s.slice(o, o + 128);
    else {
      const i = new Float32Array(s.buffer, o * Float32Array.BYTES_PER_ELEMENT, 128);
      t[n].set(i);
    }
  }
}
const En = (e, t, n, r, o) => {
  typeof e.copyToChannel == "function" ? t[n].byteLength !== 0 && e.copyToChannel(t[n], r, o) : t[n].byteLength !== 0 && e.getChannelData(r).set(t[n], o);
}, De = (e, t) => {
  const n = [];
  for (let r = 0; r < e; r += 1) {
    const o = [], s = typeof t == "number" ? t : t[r];
    for (let i = 0; i < s; i += 1)
      o.push(new Float32Array(128));
    n.push(o);
  }
  return n;
}, Lo = (e, t) => {
  const n = K(it, e), r = X(t);
  return K(n, r);
}, xo = async (e, t, n, r, o, s, i) => {
  const c = t === null ? Math.ceil(e.context.length / 128) * 128 : t.length, a = r.channelCount * r.numberOfInputs, u = o.reduce((m, h) => m + h, 0), d = u === 0 ? null : n.createBuffer(u, c, n.sampleRate);
  if (s === void 0)
    throw new Error("Missing the processor constructor.");
  const l = z(e), g = await Lo(n, e), w = De(r.numberOfInputs, r.channelCount), p = De(r.numberOfOutputs, o), f = Array.from(e.parameters.keys()).reduce((m, h) => ({ ...m, [h]: new Float32Array(128) }), {});
  for (let m = 0; m < c; m += 128) {
    if (r.numberOfInputs > 0 && t !== null)
      for (let h = 0; h < r.numberOfInputs; h += 1)
        for (let b = 0; b < r.channelCount; b += 1)
          Be(t, w[h], b, b, m);
    s.parameterDescriptors !== void 0 && t !== null && s.parameterDescriptors.forEach(({ name: h }, b) => {
      Be(t, f, h, a + b, m);
    });
    for (let h = 0; h < r.numberOfInputs; h += 1)
      for (let b = 0; b < o[h]; b += 1)
        p[h][b].byteLength === 0 && (p[h][b] = new Float32Array(128));
    try {
      const h = w.map((_, T) => l.activeInputs[T].size === 0 ? [] : _), b = i(m / n.sampleRate, n.sampleRate, () => g.process(h, p, f));
      if (d !== null)
        for (let _ = 0, T = 0; _ < r.numberOfOutputs; _ += 1) {
          for (let E = 0; E < o[_]; E += 1)
            En(d, p[_], E, T + E, m);
          T += o[_];
        }
      if (!b)
        break;
    } catch (h) {
      e.dispatchEvent(new ErrorEvent("processorerror", {
        colno: h.colno,
        filename: h.filename,
        lineno: h.lineno,
        message: h.message
      }));
      break;
    }
  }
  return d;
}, Po = (e, t, n, r, o, s, i, c, a, u, d, l, g, w, p, f) => (m, h, b) => {
  const _ = /* @__PURE__ */ new WeakMap();
  let T = null;
  const E = async (A, y) => {
    let v = d(A), M = null;
    const S = pn(v, y), N = Array.isArray(h.outputChannelCount) ? h.outputChannelCount : Array.from(h.outputChannelCount);
    if (l === null) {
      const L = N.reduce((I, U) => I + U, 0), x = o(y, {
        channelCount: Math.max(1, L),
        channelCountMode: "explicit",
        channelInterpretation: "discrete",
        numberOfOutputs: Math.max(1, L)
      }), P = [];
      for (let I = 0; I < A.numberOfOutputs; I += 1)
        P.push(r(y, {
          channelCount: 1,
          channelCountMode: "explicit",
          channelInterpretation: "speakers",
          numberOfInputs: N[I]
        }));
      const B = i(y, {
        channelCount: h.channelCount,
        channelCountMode: h.channelCountMode,
        channelInterpretation: h.channelInterpretation,
        gain: 1
      });
      B.connect = t.bind(null, P), B.disconnect = a.bind(null, P), M = [x, P, B];
    } else
      S || (v = new l(y, m));
    if (_.set(y, M === null ? v : M[2]), M !== null) {
      if (T === null) {
        if (b === void 0)
          throw new Error("Missing the processor constructor.");
        if (g === null)
          throw new Error("Missing the native OfflineAudioContext constructor.");
        const U = A.channelCount * A.numberOfInputs, W = b.parameterDescriptors === void 0 ? 0 : b.parameterDescriptors.length, O = U + W;
        T = xo(A, O === 0 ? null : await (async () => {
          const V = new g(
            O,
            // Ceil the length to the next full render quantum.
            // Bug #17: Safari does not yet expose the length.
            Math.ceil(A.context.length / 128) * 128,
            y.sampleRate
          ), G = [], fe = [];
          for (let j = 0; j < h.numberOfInputs; j += 1)
            G.push(i(V, {
              channelCount: h.channelCount,
              channelCountMode: h.channelCountMode,
              channelInterpretation: h.channelInterpretation,
              gain: 1
            })), fe.push(o(V, {
              channelCount: h.channelCount,
              channelCountMode: "explicit",
              channelInterpretation: "discrete",
              numberOfOutputs: h.channelCount
            }));
          const he = await Promise.all(Array.from(A.parameters.values()).map(async (j) => {
            const H = s(V, {
              channelCount: 1,
              channelCountMode: "explicit",
              channelInterpretation: "discrete",
              offset: j.value
            });
            return await w(V, j, H.offset), H;
          })), pe = r(V, {
            channelCount: 1,
            channelCountMode: "explicit",
            channelInterpretation: "speakers",
            numberOfInputs: Math.max(1, U + W)
          });
          for (let j = 0; j < h.numberOfInputs; j += 1) {
            G[j].connect(fe[j]);
            for (let H = 0; H < h.channelCount; H += 1)
              fe[j].connect(pe, H, j * h.channelCount + H);
          }
          for (const [j, H] of he.entries())
            H.connect(pe, 0, U + j), H.start(0);
          return pe.connect(V.destination), await Promise.all(G.map((j) => p(A, V, j))), f(V);
        })(), y, h, N, b, u);
      }
      const L = await T, x = n(y, {
        buffer: null,
        channelCount: 2,
        channelCountMode: "max",
        channelInterpretation: "speakers",
        loop: !1,
        loopEnd: 0,
        loopStart: 0,
        playbackRate: 1
      }), [P, B, I] = M;
      L !== null && (x.buffer = L, x.start(0)), x.connect(P);
      for (let U = 0, W = 0; U < A.numberOfOutputs; U += 1) {
        const O = B[U];
        for (let k = 0; k < N[U]; k += 1)
          P.connect(O, W + k, k);
        W += N[U];
      }
      return I;
    }
    if (S)
      for (const [L, x] of A.parameters.entries())
        await e(
          y,
          x,
          // @todo The definition that TypeScript uses of the AudioParamMap is lacking many methods.
          v.parameters.get(L)
        );
    else
      for (const [L, x] of A.parameters.entries())
        await w(
          y,
          x,
          // @todo The definition that TypeScript uses of the AudioParamMap is lacking many methods.
          v.parameters.get(L)
        );
    return await p(A, y, v), v;
  };
  return {
    render(A, y) {
      c(y, A);
      const v = _.get(y);
      return v !== void 0 ? Promise.resolve(v) : E(A, y);
    }
  };
}, Uo = (e, t) => (n, r) => {
  const o = t.get(n);
  if (o !== void 0)
    return o;
  const s = e.get(n);
  if (s !== void 0)
    return s;
  try {
    const i = r();
    return i instanceof Promise ? (e.set(n, i), i.catch(() => !1).then((c) => (e.delete(n), t.set(n, c), c))) : (t.set(n, i), i);
  } catch {
    return t.set(n, !1), !1;
  }
}, Bo = (e) => (t, n, r) => e(n, t, r), Do = (e) => (t, n, r = 0, o = 0) => {
  const s = t[r];
  if (s === void 0)
    throw e();
  return Ue(n) ? s.connect(n, 0, o) : s.connect(n, 0);
}, Wo = (e) => (t) => (e[0] = t, e[0]), Vo = (e, t, n, r, o, s, i, c) => (a, u) => {
  const d = t.get(a);
  if (d === void 0)
    throw new Error("Missing the expected cycle count.");
  const l = s(a.context), g = c(l);
  if (d === u) {
    if (t.delete(a), !g && i(a)) {
      const w = r(a), { outputs: p } = n(a);
      for (const f of p)
        if (Ce(f)) {
          const m = r(f[0]);
          e(w, m, f[1], f[2]);
        } else {
          const m = o(f[0]);
          w.connect(m, f[1]);
        }
    }
  } else
    t.set(a, d - u);
}, Fo = (e) => (t, n, r, o) => e(t[o], (s) => s[0] === n && s[1] === r), jo = (e) => (t, n) => {
  e(t).delete(n);
}, $o = (e) => "delayTime" in e, Go = (e, t, n) => function r(o, s) {
  const i = Pe(s) ? s : n(e, s);
  if ($o(i))
    return [];
  if (o[0] === i)
    return [o];
  if (o.includes(i))
    return [];
  const { outputs: c } = t(i);
  return Array.from(c).map((a) => r([...o, i], a[0])).reduce((a, u) => a.concat(u), []);
}, Re = (e, t, n) => {
  const r = t[n];
  if (r === void 0)
    throw e();
  return r;
}, qo = (e) => (t, n = void 0, r = void 0, o = 0) => n === void 0 ? t.forEach((s) => s.disconnect()) : typeof n == "number" ? Re(e, t, n).disconnect() : Ue(n) ? r === void 0 ? t.forEach((s) => s.disconnect(n)) : o === void 0 ? Re(e, t, r).disconnect(n, 0) : Re(e, t, r).disconnect(n, 0, o) : r === void 0 ? t.forEach((s) => s.disconnect(n)) : Re(e, t, r).disconnect(n, 0), zo = (e) => (t) => new Promise((n, r) => {
  if (e === null) {
    r(new SyntaxError());
    return;
  }
  const o = e.document.head;
  if (o === null)
    r(new SyntaxError());
  else {
    const s = e.document.createElement("script"), i = new Blob([t], { type: "application/javascript" }), c = URL.createObjectURL(i), a = e.onerror, u = () => {
      e.onerror = a, URL.revokeObjectURL(c);
    };
    e.onerror = (d, l, g, w, p) => {
      if (l === c || l === e.location.href && g === 1 && w === 1)
        return u(), r(p), !1;
      if (a !== null)
        return a(d, l, g, w, p);
    }, s.onerror = () => {
      u(), r(new SyntaxError());
    }, s.onload = () => {
      u(), n();
    }, s.src = c, s.type = "module", o.appendChild(s);
  }
}), Ho = (e) => class {
  constructor(n) {
    this._nativeEventTarget = n, this._listeners = /* @__PURE__ */ new WeakMap();
  }
  addEventListener(n, r, o) {
    if (r !== null) {
      let s = this._listeners.get(r);
      s === void 0 && (s = e(this, r), typeof r == "function" && this._listeners.set(r, s)), this._nativeEventTarget.addEventListener(n, s, o);
    }
  }
  dispatchEvent(n) {
    return this._nativeEventTarget.dispatchEvent(n);
  }
  removeEventListener(n, r, o) {
    const s = r === null ? void 0 : this._listeners.get(r);
    this._nativeEventTarget.removeEventListener(n, s === void 0 ? null : s, o);
  }
}, Yo = (e) => (t, n, r) => {
  Object.defineProperties(e, {
    currentFrame: {
      configurable: !0,
      get() {
        return Math.round(t * n);
      }
    },
    currentTime: {
      configurable: !0,
      get() {
        return t;
      }
    }
  });
  try {
    return r();
  } finally {
    e !== null && (delete e.currentFrame, delete e.currentTime);
  }
}, Xo = (e) => async (t) => {
  try {
    const n = await fetch(t);
    if (n.ok)
      return [await n.text(), n.url];
  } catch {
  }
  throw e();
}, Zo = (e, t) => (n) => t(e, n), Ko = (e) => (t) => {
  const n = e(t);
  if (n.renderer === null)
    throw new Error("Missing the renderer of the given AudioNode in the audio graph.");
  return n.renderer;
}, Jo = (e) => (t) => {
  var n;
  return (n = e.get(t)) !== null && n !== void 0 ? n : 0;
}, Qo = (e) => (t) => {
  const n = e(t);
  if (n.renderer === null)
    throw new Error("Missing the renderer of the given AudioParam in the audio graph.");
  return n.renderer;
}, es = (e) => (t) => e.get(t), Z = () => new DOMException("", "InvalidStateError"), ts = (e) => (t) => {
  const n = e.get(t);
  if (n === void 0)
    throw Z();
  return n;
}, ns = (e, t) => (n) => {
  let r = e.get(n);
  if (r !== void 0)
    return r;
  if (t === null)
    throw new Error("Missing the native OfflineAudioContext constructor.");
  return r = new t(1, 1, 44100), e.set(n, r), r;
}, rs = (e) => (t) => {
  const n = e.get(t);
  if (n === void 0)
    throw new Error("The context has no set of AudioWorkletNodes.");
  return n;
}, os = () => new DOMException("", "InvalidAccessError"), ss = (e, t, n, r, o, s) => (i) => (c, a) => {
  const u = e.get(c);
  if (u === void 0) {
    if (!i && s(c)) {
      const d = r(c), { outputs: l } = n(c);
      for (const g of l)
        if (Ce(g)) {
          const w = r(g[0]);
          t(d, w, g[1], g[2]);
        } else {
          const w = o(g[0]);
          d.disconnect(w, g[1]);
        }
    }
    e.set(c, a);
  } else
    e.set(c, u + a);
}, is = (e) => (t) => e !== null && t instanceof e, as = (e) => (t) => e !== null && typeof e.AudioNode == "function" && t instanceof e.AudioNode, cs = (e) => (t) => e !== null && typeof e.AudioParam == "function" && t instanceof e.AudioParam, us = (e) => (t) => e !== null && t instanceof e, ls = (e) => e !== null && e.isSecureContext, ds = (e, t, n, r) => class extends e {
  constructor(s, i) {
    const c = n(s), a = t(c, i);
    if (r(c))
      throw new TypeError();
    super(s, !0, a, null), this._nativeMediaStreamAudioSourceNode = a;
  }
  get mediaStream() {
    return this._nativeMediaStreamAudioSourceNode.mediaStream;
  }
}, fs = (e, t, n, r, o) => class extends r {
  constructor(i = {}) {
    if (o === null)
      throw new Error("Missing the native AudioContext constructor.");
    let c;
    try {
      c = new o(i);
    } catch (d) {
      throw d.code === 12 && d.message === "sampleRate is not in range" ? t() : d;
    }
    if (c === null)
      throw n();
    if (!go(i.latencyHint))
      throw new TypeError(`The provided value '${i.latencyHint}' is not a valid enum value of type AudioContextLatencyCategory.`);
    if (i.sampleRate !== void 0 && c.sampleRate !== i.sampleRate)
      throw t();
    super(c, 2);
    const { latencyHint: a } = i, { sampleRate: u } = c;
    if (this._baseLatency = typeof c.baseLatency == "number" ? c.baseLatency : a === "balanced" ? 512 / u : a === "interactive" || a === void 0 ? 256 / u : a === "playback" ? 1024 / u : (
      /*
       * @todo The min (256) and max (16384) values are taken from the allowed bufferSize values of a
       * ScriptProcessorNode.
       */
      Math.max(2, Math.min(128, Math.round(a * u / 128))) * 128 / u
    ), this._nativeAudioContext = c, o.name === "webkitAudioContext" ? (this._nativeGainNode = c.createGain(), this._nativeOscillatorNode = c.createOscillator(), this._nativeGainNode.gain.value = 1e-37, this._nativeOscillatorNode.connect(this._nativeGainNode).connect(c.destination), this._nativeOscillatorNode.start()) : (this._nativeGainNode = null, this._nativeOscillatorNode = null), this._state = null, c.state === "running") {
      this._state = "suspended";
      const d = () => {
        this._state === "suspended" && (this._state = null), c.removeEventListener("statechange", d);
      };
      c.addEventListener("statechange", d);
    }
  }
  get baseLatency() {
    return this._baseLatency;
  }
  get state() {
    return this._state !== null ? this._state : this._nativeAudioContext.state;
  }
  close() {
    return this.state === "closed" ? this._nativeAudioContext.close().then(() => {
      throw e();
    }) : (this._state === "suspended" && (this._state = null), this._nativeAudioContext.close().then(() => {
      this._nativeGainNode !== null && this._nativeOscillatorNode !== null && (this._nativeOscillatorNode.stop(), this._nativeGainNode.disconnect(), this._nativeOscillatorNode.disconnect()), mo(this);
    }));
  }
  resume() {
    return this._state === "suspended" ? new Promise((i, c) => {
      const a = () => {
        this._nativeAudioContext.removeEventListener("statechange", a), this._nativeAudioContext.state === "running" ? i() : this.resume().then(i, c);
      };
      this._nativeAudioContext.addEventListener("statechange", a);
    }) : this._nativeAudioContext.resume().catch((i) => {
      throw i === void 0 || i.code === 15 ? e() : i;
    });
  }
  suspend() {
    return this._nativeAudioContext.suspend().catch((i) => {
      throw i === void 0 ? e() : i;
    });
  }
}, hs = (e, t, n, r, o, s) => class extends n {
  constructor(c, a) {
    super(c), this._nativeContext = c, un.set(this, c), r(c) && o.set(c, /* @__PURE__ */ new Set()), this._destination = new e(this, a), this._listener = t(this, c), this._onstatechange = null;
  }
  get currentTime() {
    return this._nativeContext.currentTime;
  }
  get destination() {
    return this._destination;
  }
  get listener() {
    return this._listener;
  }
  get onstatechange() {
    return this._onstatechange;
  }
  set onstatechange(c) {
    const a = typeof c == "function" ? s(this, c) : null;
    this._nativeContext.onstatechange = a;
    const u = this._nativeContext.onstatechange;
    this._onstatechange = u !== null && u === a ? c : u;
  }
  get sampleRate() {
    return this._nativeContext.sampleRate;
  }
  get state() {
    return this._nativeContext.state;
  }
}, Ht = (e) => {
  const t = new Uint32Array([1179011410, 40, 1163280727, 544501094, 16, 131073, 44100, 176400, 1048580, 1635017060, 4, 0]);
  try {
    const n = e.decodeAudioData(t.buffer, () => {
    });
    return n === void 0 ? !1 : (n.catch(() => {
    }), !0);
  } catch {
  }
  return !1;
}, ps = (e, t) => (n, r, o) => {
  const s = /* @__PURE__ */ new Set();
  return n.connect = ((i) => (c, a = 0, u = 0) => {
    const d = s.size === 0;
    if (t(c))
      return i.call(n, c, a, u), e(s, [c, a, u], (l) => l[0] === c && l[1] === a && l[2] === u, !0), d && r(), c;
    i.call(n, c, a), e(s, [c, a], (l) => l[0] === c && l[1] === a, !0), d && r();
  })(n.connect), n.disconnect = ((i) => (c, a, u) => {
    const d = s.size > 0;
    if (c === void 0)
      i.apply(n), s.clear();
    else if (typeof c == "number") {
      i.call(n, c);
      for (const g of s)
        g[1] === c && s.delete(g);
    } else {
      t(c) ? i.call(n, c, a, u) : i.call(n, c, a);
      for (const g of s)
        g[0] === c && (a === void 0 || g[1] === a) && (u === void 0 || g[2] === u) && s.delete(g);
    }
    const l = s.size === 0;
    d && l && o();
  })(n.disconnect), n;
}, se = (e, t, n) => {
  const r = t[n];
  r !== void 0 && r !== e[n] && (e[n] = r);
}, Te = (e, t) => {
  se(e, t, "channelCount"), se(e, t, "channelCountMode"), se(e, t, "channelInterpretation");
}, ms = (e) => e === null ? null : e.hasOwnProperty("AudioBuffer") ? e.AudioBuffer : null, wt = (e, t, n) => {
  const r = t[n];
  r !== void 0 && r !== e[n].value && (e[n].value = r);
}, gs = (e) => {
  e.start = ((t) => {
    let n = !1;
    return (r = 0, o = 0, s) => {
      if (n)
        throw Z();
      t.call(e, r, o, s), n = !0;
    };
  })(e.start);
}, An = (e) => {
  e.start = ((t) => (n = 0, r = 0, o) => {
    if (typeof o == "number" && o < 0 || r < 0 || n < 0)
      throw new RangeError("The parameters can't be negative.");
    t.call(e, n, r, o);
  })(e.start);
}, bn = (e) => {
  e.stop = ((t) => (n = 0) => {
    if (n < 0)
      throw new RangeError("The parameter can't be negative.");
    t.call(e, n);
  })(e.stop);
}, ws = (e, t, n, r, o, s, i, c, a, u, d) => (l, g) => {
  const w = l.createBufferSource();
  return Te(w, g), wt(w, g, "playbackRate"), se(w, g, "buffer"), se(w, g, "loop"), se(w, g, "loopEnd"), se(w, g, "loopStart"), t(n, () => n(l)) || gs(w), t(r, () => r(l)) || a(w), t(o, () => o(l)) || u(w, l), t(s, () => s(l)) || An(w), t(i, () => i(l)) || d(w, l), t(c, () => c(l)) || bn(w), e(l, w), w;
}, vs = (e) => e === null ? null : e.hasOwnProperty("AudioContext") ? e.AudioContext : e.hasOwnProperty("webkitAudioContext") ? e.webkitAudioContext : null, _s = (e, t) => (n, r, o) => {
  const s = n.destination;
  if (s.channelCount !== r)
    try {
      s.channelCount = r;
    } catch {
    }
  o && s.channelCountMode !== "explicit" && (s.channelCountMode = "explicit"), s.maxChannelCount === 0 && Object.defineProperty(s, "maxChannelCount", {
    value: r
  });
  const i = e(n, {
    channelCount: r,
    channelCountMode: s.channelCountMode,
    channelInterpretation: s.channelInterpretation,
    gain: 1
  });
  return t(i, "channelCount", (c) => () => c.call(i), (c) => (a) => {
    c.call(i, a);
    try {
      s.channelCount = a;
    } catch (u) {
      if (a > s.maxChannelCount)
        throw u;
    }
  }), t(i, "channelCountMode", (c) => () => c.call(i), (c) => (a) => {
    c.call(i, a), s.channelCountMode = a;
  }), t(i, "channelInterpretation", (c) => () => c.call(i), (c) => (a) => {
    c.call(i, a), s.channelInterpretation = a;
  }), Object.defineProperty(i, "maxChannelCount", {
    get: () => s.maxChannelCount
  }), i.connect(s), i;
}, ys = (e) => e === null ? null : e.hasOwnProperty("AudioWorkletNode") ? e.AudioWorkletNode : null, Es = (e) => {
  const { port1: t } = new MessageChannel();
  try {
    t.postMessage(e);
  } finally {
    t.close();
  }
}, As = (e, t, n, r, o) => (s, i, c, a, u, d) => {
  if (c !== null)
    try {
      const l = new c(s, a, d), g = /* @__PURE__ */ new Map();
      let w = null;
      if (Object.defineProperties(l, {
        /*
         * Bug #61: Overwriting the property accessors for channelCount and channelCountMode is necessary as long as some
         * browsers have no native implementation to achieve a consistent behavior.
         */
        channelCount: {
          get: () => d.channelCount,
          set: () => {
            throw e();
          }
        },
        channelCountMode: {
          get: () => "explicit",
          set: () => {
            throw e();
          }
        },
        // Bug #156: Chrome and Edge do not yet fire an ErrorEvent.
        onprocessorerror: {
          get: () => w,
          set: (p) => {
            typeof w == "function" && l.removeEventListener("processorerror", w), w = typeof p == "function" ? p : null, typeof w == "function" && l.addEventListener("processorerror", w);
          }
        }
      }), l.addEventListener = ((p) => (...f) => {
        if (f[0] === "processorerror") {
          const m = typeof f[1] == "function" ? f[1] : typeof f[1] == "object" && f[1] !== null && typeof f[1].handleEvent == "function" ? f[1].handleEvent : null;
          if (m !== null) {
            const h = g.get(f[1]);
            h !== void 0 ? f[1] = h : (f[1] = (b) => {
              b.type === "error" ? (Object.defineProperties(b, {
                type: { value: "processorerror" }
              }), m(b)) : m(new ErrorEvent(f[0], { ...b }));
            }, g.set(m, f[1]));
          }
        }
        return p.call(l, "error", f[1], f[2]), p.call(l, ...f);
      })(l.addEventListener), l.removeEventListener = ((p) => (...f) => {
        if (f[0] === "processorerror") {
          const m = g.get(f[1]);
          m !== void 0 && (g.delete(f[1]), f[1] = m);
        }
        return p.call(l, "error", f[1], f[2]), p.call(l, f[0], f[1], f[2]);
      })(l.removeEventListener), d.numberOfOutputs !== 0) {
        const p = n(s, {
          channelCount: 1,
          channelCountMode: "explicit",
          channelInterpretation: "discrete",
          gain: 0
        });
        return l.connect(p).connect(s.destination), o(l, () => p.disconnect(), () => p.connect(s.destination));
      }
      return l;
    } catch (l) {
      throw l.code === 11 ? r() : l;
    }
  if (u === void 0)
    throw r();
  return Es(d), t(s, i, u, d);
}, bs = (e, t) => e === null ? 512 : Math.max(512, Math.min(16384, Math.pow(2, Math.round(Math.log2(e * t))))), Cs = (e) => new Promise((t, n) => {
  const { port1: r, port2: o } = new MessageChannel();
  r.onmessage = ({ data: s }) => {
    r.close(), o.close(), t(s);
  }, r.onmessageerror = ({ data: s }) => {
    r.close(), o.close(), n(s);
  }, o.postMessage(e);
}), Ts = async (e, t) => {
  const n = await Cs(t);
  return new e(n);
}, Ms = (e, t, n, r) => {
  let o = it.get(e);
  o === void 0 && (o = /* @__PURE__ */ new WeakMap(), it.set(e, o));
  const s = Ts(n, r);
  return o.set(t, s), s;
}, Ns = (e, t, n, r, o, s, i, c, a, u, d, l, g) => (w, p, f, m) => {
  if (m.numberOfInputs === 0 && m.numberOfOutputs === 0)
    throw a();
  const h = Array.isArray(m.outputChannelCount) ? m.outputChannelCount : Array.from(m.outputChannelCount);
  if (h.some((C) => C < 1))
    throw a();
  if (h.length !== m.numberOfOutputs)
    throw t();
  if (m.channelCountMode !== "explicit")
    throw a();
  const b = m.channelCount * m.numberOfInputs, _ = h.reduce((C, R) => C + R, 0), T = f.parameterDescriptors === void 0 ? 0 : f.parameterDescriptors.length;
  if (b + T > 6 || _ > 6)
    throw a();
  const E = new MessageChannel(), A = [], y = [];
  for (let C = 0; C < m.numberOfInputs; C += 1)
    A.push(i(w, {
      channelCount: m.channelCount,
      channelCountMode: m.channelCountMode,
      channelInterpretation: m.channelInterpretation,
      gain: 1
    })), y.push(o(w, {
      channelCount: m.channelCount,
      channelCountMode: "explicit",
      channelInterpretation: "discrete",
      numberOfOutputs: m.channelCount
    }));
  const v = [];
  if (f.parameterDescriptors !== void 0)
    for (const { defaultValue: C, maxValue: R, minValue: q, name: F } of f.parameterDescriptors) {
      const D = s(w, {
        channelCount: 1,
        channelCountMode: "explicit",
        channelInterpretation: "discrete",
        offset: m.parameterData[F] !== void 0 ? m.parameterData[F] : C === void 0 ? 0 : C
      });
      Object.defineProperties(D.offset, {
        defaultValue: {
          get: () => C === void 0 ? 0 : C
        },
        maxValue: {
          get: () => R === void 0 ? pt : R
        },
        minValue: {
          get: () => q === void 0 ? je : q
        }
      }), v.push(D);
    }
  const M = r(w, {
    channelCount: 1,
    channelCountMode: "explicit",
    channelInterpretation: "speakers",
    numberOfInputs: Math.max(1, b + T)
  }), S = bs(p, w.sampleRate), N = c(
    w,
    S,
    b + T,
    // Bug #87: Only Firefox will fire an AudioProcessingEvent if there is no connected output.
    Math.max(1, _)
  ), L = o(w, {
    channelCount: Math.max(1, _),
    channelCountMode: "explicit",
    channelInterpretation: "discrete",
    numberOfOutputs: Math.max(1, _)
  }), x = [];
  for (let C = 0; C < m.numberOfOutputs; C += 1)
    x.push(r(w, {
      channelCount: 1,
      channelCountMode: "explicit",
      channelInterpretation: "speakers",
      numberOfInputs: h[C]
    }));
  for (let C = 0; C < m.numberOfInputs; C += 1) {
    A[C].connect(y[C]);
    for (let R = 0; R < m.channelCount; R += 1)
      y[C].connect(M, R, C * m.channelCount + R);
  }
  const P = new yn(f.parameterDescriptors === void 0 ? [] : f.parameterDescriptors.map(({ name: C }, R) => {
    const q = v[R];
    return q.connect(M, 0, b + R), q.start(0), [C, q.offset];
  }));
  M.connect(N);
  let B = m.channelInterpretation, I = null;
  const U = m.numberOfOutputs === 0 ? [N] : x, W = {
    get bufferSize() {
      return S;
    },
    get channelCount() {
      return m.channelCount;
    },
    set channelCount(C) {
      throw n();
    },
    get channelCountMode() {
      return m.channelCountMode;
    },
    set channelCountMode(C) {
      throw n();
    },
    get channelInterpretation() {
      return B;
    },
    set channelInterpretation(C) {
      for (const R of A)
        R.channelInterpretation = C;
      B = C;
    },
    get context() {
      return N.context;
    },
    get inputs() {
      return A;
    },
    get numberOfInputs() {
      return m.numberOfInputs;
    },
    get numberOfOutputs() {
      return m.numberOfOutputs;
    },
    get onprocessorerror() {
      return I;
    },
    set onprocessorerror(C) {
      typeof I == "function" && W.removeEventListener("processorerror", I), I = typeof C == "function" ? C : null, typeof I == "function" && W.addEventListener("processorerror", I);
    },
    get parameters() {
      return P;
    },
    get port() {
      return E.port2;
    },
    addEventListener(...C) {
      return N.addEventListener(C[0], C[1], C[2]);
    },
    connect: e.bind(null, U),
    disconnect: u.bind(null, U),
    dispatchEvent(...C) {
      return N.dispatchEvent(C[0]);
    },
    removeEventListener(...C) {
      return N.removeEventListener(C[0], C[1], C[2]);
    }
  }, O = /* @__PURE__ */ new Map();
  E.port1.addEventListener = ((C) => (...R) => {
    if (R[0] === "message") {
      const q = typeof R[1] == "function" ? R[1] : typeof R[1] == "object" && R[1] !== null && typeof R[1].handleEvent == "function" ? R[1].handleEvent : null;
      if (q !== null) {
        const F = O.get(R[1]);
        F !== void 0 ? R[1] = F : (R[1] = (D) => {
          d(w.currentTime, w.sampleRate, () => q(D));
        }, O.set(q, R[1]));
      }
    }
    return C.call(E.port1, R[0], R[1], R[2]);
  })(E.port1.addEventListener), E.port1.removeEventListener = ((C) => (...R) => {
    if (R[0] === "message") {
      const q = O.get(R[1]);
      q !== void 0 && (O.delete(R[1]), R[1] = q);
    }
    return C.call(E.port1, R[0], R[1], R[2]);
  })(E.port1.removeEventListener);
  let k = null;
  Object.defineProperty(E.port1, "onmessage", {
    get: () => k,
    set: (C) => {
      typeof k == "function" && E.port1.removeEventListener("message", k), k = typeof C == "function" ? C : null, typeof k == "function" && (E.port1.addEventListener("message", k), E.port1.start());
    }
  }), f.prototype.port = E.port1;
  let V = null;
  Ms(w, W, f, m).then((C) => V = C);
  const fe = De(m.numberOfInputs, m.channelCount), he = De(m.numberOfOutputs, h), pe = f.parameterDescriptors === void 0 ? [] : f.parameterDescriptors.reduce((C, { name: R }) => ({ ...C, [R]: new Float32Array(128) }), {});
  let j = !0;
  const H = () => {
    m.numberOfOutputs > 0 && N.disconnect(L);
    for (let C = 0, R = 0; C < m.numberOfOutputs; C += 1) {
      const q = x[C];
      for (let F = 0; F < h[C]; F += 1)
        L.disconnect(q, R + F, F);
      R += h[C];
    }
  }, Me = /* @__PURE__ */ new Map();
  N.onaudioprocess = ({ inputBuffer: C, outputBuffer: R }) => {
    if (V !== null) {
      const q = l(W);
      for (let F = 0; F < S; F += 128) {
        for (let D = 0; D < m.numberOfInputs; D += 1)
          for (let $ = 0; $ < m.channelCount; $ += 1)
            Be(C, fe[D], $, $, F);
        f.parameterDescriptors !== void 0 && f.parameterDescriptors.forEach(({ name: D }, $) => {
          Be(C, pe, D, b + $, F);
        });
        for (let D = 0; D < m.numberOfInputs; D += 1)
          for (let $ = 0; $ < h[D]; $ += 1)
            he[D][$].byteLength === 0 && (he[D][$] = new Float32Array(128));
        try {
          const D = fe.map((Y, te) => {
            if (q[te].size > 0)
              return Me.set(te, S / 128), Y;
            const Ke = Me.get(te);
            return Ke === void 0 ? [] : (Y.every((Zn) => Zn.every((Kn) => Kn === 0)) && (Ke === 1 ? Me.delete(te) : Me.set(te, Ke - 1)), Y);
          });
          j = d(w.currentTime + F / w.sampleRate, w.sampleRate, () => V.process(D, he, pe));
          for (let Y = 0, te = 0; Y < m.numberOfOutputs; Y += 1) {
            for (let _e = 0; _e < h[Y]; _e += 1)
              En(R, he[Y], _e, te + _e, F);
            te += h[Y];
          }
        } catch (D) {
          j = !1, W.dispatchEvent(new ErrorEvent("processorerror", {
            colno: D.colno,
            filename: D.filename,
            lineno: D.lineno,
            message: D.message
          }));
        }
        if (!j) {
          for (let D = 0; D < m.numberOfInputs; D += 1) {
            A[D].disconnect(y[D]);
            for (let $ = 0; $ < m.channelCount; $ += 1)
              y[F].disconnect(M, $, D * m.channelCount + $);
          }
          if (f.parameterDescriptors !== void 0) {
            const D = f.parameterDescriptors.length;
            for (let $ = 0; $ < D; $ += 1) {
              const Y = v[$];
              Y.disconnect(M, 0, b + $), Y.stop();
            }
          }
          M.disconnect(N), N.onaudioprocess = null, Xe ? H() : Ot();
          break;
        }
      }
    }
  };
  let Xe = !1;
  const Ze = i(w, {
    channelCount: 1,
    channelCountMode: "explicit",
    channelInterpretation: "discrete",
    gain: 0
  }), Nt = () => N.connect(Ze).connect(w.destination), Ot = () => {
    N.disconnect(Ze), Ze.disconnect();
  }, Yn = () => {
    if (j) {
      Ot(), m.numberOfOutputs > 0 && N.connect(L);
      for (let C = 0, R = 0; C < m.numberOfOutputs; C += 1) {
        const q = x[C];
        for (let F = 0; F < h[C]; F += 1)
          L.connect(q, R + F, F);
        R += h[C];
      }
    }
    Xe = !0;
  }, Xn = () => {
    j && (Nt(), H()), Xe = !1;
  };
  return Nt(), g(W, Yn, Xn);
}, Os = (e, t) => (n, r) => {
  const o = n.createChannelMerger(r.numberOfInputs);
  return e !== null && e.name === "webkitAudioContext" && t(n, o), Te(o, r), o;
}, Rs = (e) => {
  const t = e.numberOfOutputs;
  Object.defineProperty(e, "channelCount", {
    get: () => t,
    set: (n) => {
      if (n !== t)
        throw Z();
    }
  }), Object.defineProperty(e, "channelCountMode", {
    get: () => "explicit",
    set: (n) => {
      if (n !== "explicit")
        throw Z();
    }
  }), Object.defineProperty(e, "channelInterpretation", {
    get: () => "discrete",
    set: (n) => {
      if (n !== "discrete")
        throw Z();
    }
  });
}, Cn = (e, t) => {
  const n = e.createChannelSplitter(t.numberOfOutputs);
  return Te(n, t), Rs(n), n;
}, Is = (e, t, n, r, o) => (s, i) => {
  if (s.createConstantSource === void 0)
    return n(s, i);
  const c = s.createConstantSource();
  return Te(c, i), wt(c, i, "offset"), t(r, () => r(s)) || An(c), t(o, () => o(s)) || bn(c), e(s, c), c;
}, Tn = (e, t) => (e.connect = t.connect.bind(t), e.disconnect = t.disconnect.bind(t), e), Ss = (e, t, n, r) => (o, { offset: s, ...i }) => {
  const c = o.createBuffer(1, 2, 44100), a = t(o, {
    buffer: null,
    channelCount: 2,
    channelCountMode: "max",
    channelInterpretation: "speakers",
    loop: !1,
    loopEnd: 0,
    loopStart: 0,
    playbackRate: 1
  }), u = n(o, { ...i, gain: s }), d = c.getChannelData(0);
  d[0] = 1, d[1] = 1, a.buffer = c, a.loop = !0;
  const l = {
    get bufferSize() {
    },
    get channelCount() {
      return u.channelCount;
    },
    set channelCount(p) {
      u.channelCount = p;
    },
    get channelCountMode() {
      return u.channelCountMode;
    },
    set channelCountMode(p) {
      u.channelCountMode = p;
    },
    get channelInterpretation() {
      return u.channelInterpretation;
    },
    set channelInterpretation(p) {
      u.channelInterpretation = p;
    },
    get context() {
      return u.context;
    },
    get inputs() {
      return [];
    },
    get numberOfInputs() {
      return a.numberOfInputs;
    },
    get numberOfOutputs() {
      return u.numberOfOutputs;
    },
    get offset() {
      return u.gain;
    },
    get onended() {
      return a.onended;
    },
    set onended(p) {
      a.onended = p;
    },
    addEventListener(...p) {
      return a.addEventListener(p[0], p[1], p[2]);
    },
    dispatchEvent(...p) {
      return a.dispatchEvent(p[0]);
    },
    removeEventListener(...p) {
      return a.removeEventListener(p[0], p[1], p[2]);
    },
    start(p = 0) {
      a.start.call(a, p);
    },
    stop(p = 0) {
      a.stop.call(a, p);
    }
  }, g = () => a.connect(u), w = () => a.disconnect(u);
  return e(o, a), r(Tn(l, u), g, w);
}, oe = (e, t) => {
  const n = e.createGain();
  return Te(n, t), wt(n, t, "gain"), n;
}, ks = (e, { mediaStream: t }) => {
  const n = t.getAudioTracks();
  n.sort((s, i) => s.id < i.id ? -1 : s.id > i.id ? 1 : 0);
  const r = n.slice(0, 1), o = e.createMediaStreamSource(new MediaStream(r));
  return Object.defineProperty(o, "mediaStream", { value: t }), o;
}, Ls = (e) => e === null ? null : e.hasOwnProperty("OfflineAudioContext") ? e.OfflineAudioContext : e.hasOwnProperty("webkitOfflineAudioContext") ? e.webkitOfflineAudioContext : null, vt = (e, t, n, r) => e.createScriptProcessor(t, n, r), de = () => new DOMException("", "NotSupportedError"), xs = (e, t) => (n, r, o) => (e(r).replay(o), t(r, n, o)), Ps = (e, t, n) => async (r, o, s) => {
  const i = e(r);
  await Promise.all(i.activeInputs.map((c, a) => Array.from(c).map(async ([u, d]) => {
    const g = await t(u).render(u, o), w = r.context.destination;
    !n(u) && (r !== w || !n(r)) && g.connect(s, d, a);
  })).reduce((c, a) => [...c, ...a], []));
}, Us = (e, t, n) => async (r, o, s) => {
  const i = t(r);
  await Promise.all(Array.from(i.activeInputs).map(async ([c, a]) => {
    const d = await e(c).render(c, o);
    n(c) || d.connect(s, a);
  }));
}, Bs = (e, t, n, r) => (o) => e(Ht, () => Ht(o)) ? Promise.resolve(e(r, r)).then((s) => {
  if (!s) {
    const i = n(o, 512, 0, 1);
    o.oncomplete = () => {
      i.onaudioprocess = null, i.disconnect();
    }, i.onaudioprocess = () => o.currentTime, i.connect(o.destination);
  }
  return o.startRendering();
}) : new Promise((s) => {
  const i = t(o, {
    channelCount: 1,
    channelCountMode: "explicit",
    channelInterpretation: "discrete",
    gain: 0
  });
  o.oncomplete = (c) => {
    i.disconnect(), s(c.renderedBuffer);
  }, i.connect(o.destination), o.startRendering();
}), Ds = (e) => (t, n) => {
  e.set(t, n);
}, Ws = (e) => () => {
  if (e === null)
    return !1;
  try {
    new e({ length: 1, sampleRate: 44100 });
  } catch {
    return !1;
  }
  return !0;
}, Vs = (e, t) => async () => {
  if (e === null)
    return !0;
  if (t === null)
    return !1;
  const n = new Blob(['class A extends AudioWorkletProcessor{process(i){this.port.postMessage(i,[i[0][0].buffer])}}registerProcessor("a",A)'], {
    type: "application/javascript; charset=utf-8"
  }), r = new t(1, 128, 44100), o = URL.createObjectURL(n);
  let s = !1, i = !1;
  try {
    await r.audioWorklet.addModule(o);
    const c = new e(r, "a", { numberOfOutputs: 0 }), a = r.createOscillator();
    c.port.onmessage = () => s = !0, c.onprocessorerror = () => i = !0, a.connect(c), a.start(0), await r.startRendering(), await new Promise((u) => setTimeout(u));
  } catch {
  } finally {
    URL.revokeObjectURL(o);
  }
  return s && !i;
}, Fs = (e, t) => () => {
  if (t === null)
    return Promise.resolve(!1);
  const n = new t(1, 1, 44100), r = e(n, {
    channelCount: 1,
    channelCountMode: "explicit",
    channelInterpretation: "discrete",
    gain: 0
  });
  return new Promise((o) => {
    n.oncomplete = () => {
      r.disconnect(), o(n.currentTime !== 0);
    }, n.startRendering();
  });
}, js = () => new DOMException("", "UnknownError"), $s = () => typeof window > "u" ? null : window, Gs = (e, t) => (n) => {
  n.copyFromChannel = (r, o, s = 0) => {
    const i = e(s), c = e(o);
    if (c >= n.numberOfChannels)
      throw t();
    const a = n.length, u = n.getChannelData(c), d = r.length;
    for (let l = i < 0 ? -i : 0; l + i < a && l < d; l += 1)
      r[l] = u[l + i];
  }, n.copyToChannel = (r, o, s = 0) => {
    const i = e(s), c = e(o);
    if (c >= n.numberOfChannels)
      throw t();
    const a = n.length, u = n.getChannelData(c), d = r.length;
    for (let l = i < 0 ? -i : 0; l + i < a && l < d; l += 1)
      u[l + i] = r[l];
  };
}, qs = (e) => (t) => {
  t.copyFromChannel = ((n) => (r, o, s = 0) => {
    const i = e(s), c = e(o);
    if (i < t.length)
      return n.call(t, r, c, i);
  })(t.copyFromChannel), t.copyToChannel = ((n) => (r, o, s = 0) => {
    const i = e(s), c = e(o);
    if (i < t.length)
      return n.call(t, r, c, i);
  })(t.copyToChannel);
}, zs = (e) => (t, n) => {
  const r = n.createBuffer(1, 1, 44100);
  t.buffer === null && (t.buffer = r), e(t, "buffer", (o) => () => {
    const s = o.call(t);
    return s === r ? null : s;
  }, (o) => (s) => o.call(t, s === null ? r : s));
}, Hs = (e, t) => (n, r) => {
  r.channelCount = 1, r.channelCountMode = "explicit", Object.defineProperty(r, "channelCount", {
    get: () => 1,
    set: () => {
      throw e();
    }
  }), Object.defineProperty(r, "channelCountMode", {
    get: () => "explicit",
    set: () => {
      throw e();
    }
  });
  const o = n.createBufferSource();
  t(r, () => {
    const c = r.numberOfInputs;
    for (let a = 0; a < c; a += 1)
      o.connect(r, 0, a);
  }, () => o.disconnect(r));
}, Ys = (e, t, n) => e.copyFromChannel === void 0 ? e.getChannelData(n)[0] : (e.copyFromChannel(t, n), t[0]), _t = (e, t, n, r) => {
  let o = e;
  for (; !o.hasOwnProperty(t); )
    o = Object.getPrototypeOf(o);
  const { get: s, set: i } = Object.getOwnPropertyDescriptor(o, t);
  Object.defineProperty(e, t, { get: n(s), set: r(i) });
}, Xs = (e) => ({
  ...e,
  outputChannelCount: e.outputChannelCount !== void 0 ? e.outputChannelCount : e.numberOfInputs === 1 && e.numberOfOutputs === 1 ? (
    /*
     * Bug #61: This should be the computedNumberOfChannels, but unfortunately that is almost impossible to fake. That's why
     * the channelCountMode is required to be 'explicit' as long as there is not a native implementation in every browser. That
     * makes sure the computedNumberOfChannels is equivilant to the channelCount which makes it much easier to compute.
     */
    [e.channelCount]
  ) : Array.from({ length: e.numberOfOutputs }, () => 1)
}), Mn = (e, t, n) => {
  try {
    e.setValueAtTime(t, n);
  } catch (r) {
    if (r.code !== 9)
      throw r;
    Mn(e, t, n + 1e-7);
  }
}, Zs = (e) => {
  const t = e.createBufferSource();
  t.start();
  try {
    t.start();
  } catch {
    return !0;
  }
  return !1;
}, Ks = (e) => {
  const t = e.createBufferSource(), n = e.createBuffer(1, 1, 44100);
  t.buffer = n;
  try {
    t.start(0, 1);
  } catch {
    return !1;
  }
  return !0;
}, Js = (e) => {
  const t = e.createBufferSource();
  t.start();
  try {
    t.stop();
  } catch {
    return !1;
  }
  return !0;
}, Nn = (e) => {
  const t = e.createOscillator();
  try {
    t.start(-1);
  } catch (n) {
    return n instanceof RangeError;
  }
  return !1;
}, Qs = (e) => {
  const t = e.createBuffer(1, 1, 44100), n = e.createBufferSource();
  n.buffer = t, n.start(), n.stop();
  try {
    return n.stop(), !0;
  } catch {
    return !1;
  }
}, On = (e) => {
  const t = e.createOscillator();
  try {
    t.stop(-1);
  } catch (n) {
    return n instanceof RangeError;
  }
  return !1;
}, ei = (e) => {
  const { port1: t, port2: n } = new MessageChannel();
  try {
    t.postMessage(e);
  } finally {
    t.close(), n.close();
  }
}, ti = (e) => {
  e.start = ((t) => (n = 0, r = 0, o) => {
    const s = e.buffer, i = s === null ? r : Math.min(s.duration, r);
    s !== null && i > s.duration - 0.5 / e.context.sampleRate ? t.call(e, n, 0, 0) : t.call(e, n, i, o);
  })(e.start);
}, ni = (e, t) => {
  const n = t.createGain();
  e.connect(n);
  const r = ((o) => () => {
    o.call(e, n), e.removeEventListener("ended", r);
  })(e.disconnect);
  e.addEventListener("ended", r), Tn(e, n), e.stop = ((o) => {
    let s = !1;
    return (i = 0) => {
      if (s)
        try {
          o.call(e, i);
        } catch {
          n.gain.setValueAtTime(0, i);
        }
      else
        o.call(e, i), s = !0;
    };
  })(e.stop);
}, $e = (e, t) => (n) => {
  const r = { value: e };
  return Object.defineProperties(n, {
    currentTarget: r,
    target: r
  }), typeof t == "function" ? t.call(e, n) : t.handleEvent.call(e, n);
}, ri = Hr(le), oi = Qr(le), si = Fo(Fe), ii = /* @__PURE__ */ new WeakMap(), ai = Jo(ii), we = Uo(/* @__PURE__ */ new Map(), /* @__PURE__ */ new WeakMap()), J = $s(), Rn = Ko(z), yt = Ps(z, Rn, ae), ce = ts(un), ve = Ls(J), ee = us(ve), In = /* @__PURE__ */ new WeakMap(), Sn = Ho($e), Ge = vs(J), ci = is(Ge), kn = as(J), ui = cs(J), Ee = ys(J), qe = Oo(Yr(on), Jr(ri, oi, ut, si, lt, z, ai, Ae, X, le, ie, ae, Ie), we, ss(ot, lt, z, X, ye, ie), ue, os, de, Vo(ut, ot, z, X, ye, ce, ie, ee), Go(In, z, K), Sn, ce, ci, kn, ui, ee, Ee), li = /* @__PURE__ */ new WeakSet(), Yt = ms(J), Ln = Wo(new Uint32Array(1)), di = Gs(Ln, ue), fi = qs(Ln), hi = oo(li, we, de, Yt, ve, Ws(Yt), di, fi), Et = eo(oe), xn = Us(Rn, be, ae), Pn = Bo(xn), ze = ws(Et, we, Zs, Ks, Js, Nn, Qs, On, ti, zs(_t), ni), Un = xs(Qo(be), xn), pi = ao(Pn, ze, X, Un, yt), At = Ro(Xr(an), In, cn, Io, Fr, jr, $r, Gr, qr, tt, nn, Ge, Mn), mi = io(qe, pi, At, Z, ze, ce, ee, $e), gi = wo(qe, vo, ue, Z, _s(oe, _t), ce, ee, yt), He = ps(le, kn), wi = Hs(Z, He), bt = Os(Ge, wi), vi = Ss(Et, ze, oe, He), Ct = Is(Et, we, vi, Nn, On), _i = Bs(we, oe, vt, Fs(oe, ve)), yi = _o(At, bt, Ct, vt, de, Ys, ee, _t), Bn = /* @__PURE__ */ new WeakMap(), Ei = hs(gi, yi, Sn, ee, Bn, $e), Dn = ls(J), Tt = Yo(J), Wn = /* @__PURE__ */ new WeakMap(), Ai = ns(Wn, ve), Xt = Dn ? Kr(
  we,
  de,
  zo(J),
  Tt,
  Xo(zr),
  ce,
  Ai,
  ee,
  Ee,
  /* @__PURE__ */ new WeakMap(),
  /* @__PURE__ */ new WeakMap(),
  Vs(Ee, ve),
  // @todo window is guaranteed to be defined because isSecureContext checks that as well.
  J
) : void 0, bi = ds(qe, ks, ce, ee), Vn = rs(Bn), Ci = to(Vn), Fn = Do(ue), Ti = jo(Vn), jn = qo(ue), $n = /* @__PURE__ */ new WeakMap(), Mi = Zo($n, K), Ni = Ns(Fn, ue, Z, bt, Cn, Ct, oe, vt, de, jn, Tt, Mi, He), Oi = As(Z, Ni, oe, de, He), Ri = Po(Pn, Fn, ze, bt, Cn, Ct, oe, Ti, jn, Tt, X, Ee, ve, Un, yt, _i), Ii = es(Wn), Si = Ds($n), Zt = Dn ? ko(Ci, qe, At, Ri, Oi, z, Ii, ce, ee, Ee, Xs, Si, ei, $e) : void 0, ki = fs(Z, de, js, Ei, Ge), Gn = "Missing AudioWorklet support. Maybe this is not running in a secure context.", Li = async (e, t, n, r, o) => {
  const { encoderId: s, port: i } = await Qt(o, t.sampleRate);
  if (Zt === void 0)
    throw new Error(Gn);
  const c = new mi(t, { buffer: e }), a = new bi(t, { mediaStream: r }), u = Br(Zt, t, { channelCount: n });
  return { audioBufferSourceNode: c, encoderId: s, mediaStreamAudioSourceNode: a, port: i, recorderAudioWorkletNode: u };
}, xi = (e, t, n, r) => (o, s, i) => {
  var c;
  const a = (c = s.getAudioTracks()[0]) === null || c === void 0 ? void 0 : c.getSettings().sampleRate, u = new ki({ latencyHint: "playback", sampleRate: a }), d = Math.max(1024, Math.ceil(u.baseLatency * u.sampleRate)), l = new hi({ length: d, sampleRate: u.sampleRate }), g = [], w = Ur((v) => {
    if (Xt === void 0)
      throw new Error(Gn);
    return Xt(u, v);
  });
  let p = null, f = null, m = null, h = null, b = !0;
  const _ = (v) => {
    o.dispatchEvent(e("dataavailable", { data: new Blob(v, { type: i }) }));
  }, T = async (v, M) => {
    const S = await Se(v, M);
    m === null ? g.push(...S) : (_(S), h = T(v, M));
  }, E = () => (b = !0, u.resume()), A = () => {
    m !== null && (p !== null && (s.removeEventListener("addtrack", p), s.removeEventListener("removetrack", p)), f !== null && clearTimeout(f), m.then(async ({ encoderId: v, mediaStreamAudioSourceNode: M, recorderAudioWorkletNode: S }) => {
      h !== null && (h.catch(() => {
      }), h = null), await S.stop(), M.disconnect(S);
      const N = await Se(v, null);
      m === null && await y(), _([...g, ...N]), g.length = 0, o.dispatchEvent(new Event("stop"));
    }), m = null);
  }, y = () => (b = !1, u.suspend());
  return y(), {
    get mimeType() {
      return i;
    },
    get state() {
      return m === null ? "inactive" : b ? "recording" : "paused";
    },
    pause() {
      if (m === null)
        throw n();
      b && (y(), o.dispatchEvent(new Event("pause")));
    },
    resume() {
      if (m === null)
        throw n();
      b || (E(), o.dispatchEvent(new Event("resume")));
    },
    start(v) {
      var M;
      if (m !== null)
        throw n();
      if (s.getVideoTracks().length > 0)
        throw r();
      o.dispatchEvent(new Event("start"));
      const S = s.getAudioTracks(), N = S.length === 0 ? 2 : (M = S[0].getSettings().channelCount) !== null && M !== void 0 ? M : 2;
      m = Promise.all([
        E(),
        w.then(() => Li(l, u, N, s, i))
      ]).then(async ([, { audioBufferSourceNode: x, encoderId: P, mediaStreamAudioSourceNode: B, port: I, recorderAudioWorkletNode: U }]) => (B.connect(U), await new Promise((W) => {
        x.onended = W, x.connect(U), x.start(u.currentTime + d / u.sampleRate);
      }), x.disconnect(U), await U.record(I), v !== void 0 && (h = T(P, v)), { encoderId: P, mediaStreamAudioSourceNode: B, recorderAudioWorkletNode: U }));
      const L = s.getTracks();
      p = () => {
        A(), o.dispatchEvent(new ErrorEvent("error", { error: t() }));
      }, s.addEventListener("addtrack", p), s.addEventListener("removetrack", p), f = setInterval(() => {
        const x = s.getTracks();
        (x.length !== L.length || x.some((P, B) => P !== L[B])) && p !== null && p();
      }, 1e3);
    },
    stop: A
  };
};
class Qe {
  constructor(t, n = 0, r) {
    if (n < 0 || r !== void 0 && r < 0)
      throw new RangeError();
    const o = t.reduce((d, l) => d + l.byteLength, 0);
    if (n > o || r !== void 0 && n + r > o)
      throw new RangeError();
    const s = [], i = r === void 0 ? o - n : r, c = [];
    let a = 0, u = n;
    for (const d of t)
      if (c.length === 0)
        if (d.byteLength > u) {
          a = d.byteLength - u;
          const l = a > i ? i : a;
          s.push(new DataView(d, u, l)), c.push(d);
        } else
          u -= d.byteLength;
      else if (a < i) {
        a += d.byteLength;
        const l = a > i ? d.byteLength - a + i : d.byteLength;
        s.push(new DataView(d, 0, l)), c.push(d);
      }
    this._buffers = c, this._byteLength = i, this._byteOffset = u, this._dataViews = s, this._internalBuffer = new DataView(new ArrayBuffer(8));
  }
  get buffers() {
    return this._buffers;
  }
  get byteLength() {
    return this._byteLength;
  }
  get byteOffset() {
    return this._byteOffset;
  }
  getFloat32(t, n) {
    return this._internalBuffer.setUint8(0, this.getUint8(t + 0)), this._internalBuffer.setUint8(1, this.getUint8(t + 1)), this._internalBuffer.setUint8(2, this.getUint8(t + 2)), this._internalBuffer.setUint8(3, this.getUint8(t + 3)), this._internalBuffer.getFloat32(0, n);
  }
  getFloat64(t, n) {
    return this._internalBuffer.setUint8(0, this.getUint8(t + 0)), this._internalBuffer.setUint8(1, this.getUint8(t + 1)), this._internalBuffer.setUint8(2, this.getUint8(t + 2)), this._internalBuffer.setUint8(3, this.getUint8(t + 3)), this._internalBuffer.setUint8(4, this.getUint8(t + 4)), this._internalBuffer.setUint8(5, this.getUint8(t + 5)), this._internalBuffer.setUint8(6, this.getUint8(t + 6)), this._internalBuffer.setUint8(7, this.getUint8(t + 7)), this._internalBuffer.getFloat64(0, n);
  }
  getInt16(t, n) {
    return this._internalBuffer.setUint8(0, this.getUint8(t + 0)), this._internalBuffer.setUint8(1, this.getUint8(t + 1)), this._internalBuffer.getInt16(0, n);
  }
  getInt32(t, n) {
    return this._internalBuffer.setUint8(0, this.getUint8(t + 0)), this._internalBuffer.setUint8(1, this.getUint8(t + 1)), this._internalBuffer.setUint8(2, this.getUint8(t + 2)), this._internalBuffer.setUint8(3, this.getUint8(t + 3)), this._internalBuffer.getInt32(0, n);
  }
  getInt8(t) {
    const [n, r] = this._findDataViewWithOffset(t);
    return n.getInt8(t - r);
  }
  getUint16(t, n) {
    return this._internalBuffer.setUint8(0, this.getUint8(t + 0)), this._internalBuffer.setUint8(1, this.getUint8(t + 1)), this._internalBuffer.getUint16(0, n);
  }
  getUint32(t, n) {
    return this._internalBuffer.setUint8(0, this.getUint8(t + 0)), this._internalBuffer.setUint8(1, this.getUint8(t + 1)), this._internalBuffer.setUint8(2, this.getUint8(t + 2)), this._internalBuffer.setUint8(3, this.getUint8(t + 3)), this._internalBuffer.getUint32(0, n);
  }
  getUint8(t) {
    const [n, r] = this._findDataViewWithOffset(t);
    return n.getUint8(t - r);
  }
  setFloat32(t, n, r) {
    this._internalBuffer.setFloat32(0, n, r), this.setUint8(t, this._internalBuffer.getUint8(0)), this.setUint8(t + 1, this._internalBuffer.getUint8(1)), this.setUint8(t + 2, this._internalBuffer.getUint8(2)), this.setUint8(t + 3, this._internalBuffer.getUint8(3));
  }
  setFloat64(t, n, r) {
    this._internalBuffer.setFloat64(0, n, r), this.setUint8(t, this._internalBuffer.getUint8(0)), this.setUint8(t + 1, this._internalBuffer.getUint8(1)), this.setUint8(t + 2, this._internalBuffer.getUint8(2)), this.setUint8(t + 3, this._internalBuffer.getUint8(3)), this.setUint8(t + 4, this._internalBuffer.getUint8(4)), this.setUint8(t + 5, this._internalBuffer.getUint8(5)), this.setUint8(t + 6, this._internalBuffer.getUint8(6)), this.setUint8(t + 7, this._internalBuffer.getUint8(7));
  }
  setInt16(t, n, r) {
    this._internalBuffer.setInt16(0, n, r), this.setUint8(t, this._internalBuffer.getUint8(0)), this.setUint8(t + 1, this._internalBuffer.getUint8(1));
  }
  setInt32(t, n, r) {
    this._internalBuffer.setInt32(0, n, r), this.setUint8(t, this._internalBuffer.getUint8(0)), this.setUint8(t + 1, this._internalBuffer.getUint8(1)), this.setUint8(t + 2, this._internalBuffer.getUint8(2)), this.setUint8(t + 3, this._internalBuffer.getUint8(3));
  }
  setInt8(t, n) {
    const [r, o] = this._findDataViewWithOffset(t);
    r.setInt8(t - o, n);
  }
  setUint16(t, n, r) {
    this._internalBuffer.setUint16(0, n, r), this.setUint8(t, this._internalBuffer.getUint8(0)), this.setUint8(t + 1, this._internalBuffer.getUint8(1));
  }
  setUint32(t, n, r) {
    this._internalBuffer.setUint32(0, n, r), this.setUint8(t, this._internalBuffer.getUint8(0)), this.setUint8(t + 1, this._internalBuffer.getUint8(1)), this.setUint8(t + 2, this._internalBuffer.getUint8(2)), this.setUint8(t + 3, this._internalBuffer.getUint8(3));
  }
  setUint8(t, n) {
    const [r, o] = this._findDataViewWithOffset(t);
    r.setUint8(t - o, n);
  }
  _findDataViewWithOffset(t) {
    let n = 0;
    for (const r of this._dataViews) {
      const o = n + r.byteLength;
      if (t >= n && t < o)
        return [r, n];
      n = o;
    }
    throw new RangeError();
  }
}
const Pi = (e, t, n) => (r, o, s, i) => {
  const c = [], a = new o(s, { mimeType: "audio/webm;codecs=pcm" });
  let u = null, d = () => {
  };
  const l = (p) => {
    r.dispatchEvent(e("dataavailable", { data: new Blob(p, { type: i }) }));
  }, g = async (p, f) => {
    const m = await Se(p, f);
    a.state === "inactive" ? c.push(...m) : (l(m), u = g(p, f));
  }, w = () => {
    a.state !== "inactive" && (u !== null && (u.catch(() => {
    }), u = null), d(), d = () => {
    }, a.stop());
  };
  return a.addEventListener("error", (p) => {
    w(), r.dispatchEvent(new ErrorEvent("error", {
      error: p.error
    }));
  }), a.addEventListener("pause", () => r.dispatchEvent(new Event("pause"))), a.addEventListener("resume", () => r.dispatchEvent(new Event("resume"))), a.addEventListener("start", () => r.dispatchEvent(new Event("start"))), {
    get mimeType() {
      return i;
    },
    get state() {
      return a.state;
    },
    pause() {
      return a.pause();
    },
    resume() {
      return a.resume();
    },
    start(p) {
      const [f] = s.getAudioTracks();
      if (f !== void 0 && a.state === "inactive") {
        const { channelCount: m, sampleRate: h } = f.getSettings();
        if (m === void 0)
          throw new Error("The channelCount is not defined.");
        if (h === void 0)
          throw new Error("The sampleRate is not defined.");
        let b = !1, _ = !1, T = 0, E = Qt(i, h);
        d = () => {
          _ = !0;
        };
        const A = en(a, "dataavailable")(({ data: y }) => {
          T += 1;
          const v = y.arrayBuffer();
          E = E.then(async ({ dataView: M = null, elementType: S = null, encoderId: N, port: L }) => {
            const x = await v;
            T -= 1;
            const P = M === null ? new Qe([x]) : new Qe([...M.buffers, x], M.byteOffset);
            if (!b && a.state === "recording" && !_) {
              const O = n(P, 0);
              if (O === null)
                return { dataView: P, elementType: S, encoderId: N, port: L };
              const { value: k } = O;
              if (k !== 172351395)
                return { dataView: M, elementType: S, encoderId: N, port: L };
              b = !0;
            }
            const { currentElementType: B, offset: I, contents: U } = t(P, S, m), W = I < P.byteLength ? new Qe(P.buffers, P.byteOffset + I) : null;
            return U.forEach((O) => L.postMessage(O, O.map(({ buffer: k }) => k))), T === 0 && (a.state === "inactive" || _) && (Se(N, null).then((O) => {
              l([...c, ...O]), c.length = 0, r.dispatchEvent(new Event("stop"));
            }), L.postMessage([]), L.close(), A()), { dataView: W, elementType: B, encoderId: N, port: L };
          });
        });
        p !== void 0 && E.then(({ encoderId: y }) => u = g(y, p));
      }
      a.start(100);
    },
    stop: w
  };
}, Ui = () => typeof window > "u" ? null : window, qn = (e, t) => {
  if (t >= e.byteLength)
    return null;
  const n = e.getUint8(t);
  if (n > 127)
    return 1;
  if (n > 63)
    return 2;
  if (n > 31)
    return 3;
  if (n > 15)
    return 4;
  if (n > 7)
    return 5;
  if (n > 3)
    return 6;
  if (n > 1)
    return 7;
  if (n > 0)
    return 8;
  const r = qn(e, t + 1);
  return r === null ? null : r + 8;
}, Bi = (e, t) => (n) => {
  const r = { value: e };
  return Object.defineProperties(n, {
    currentTarget: r,
    target: r
  }), typeof t == "function" ? t.call(e, n) : t.handleEvent.call(e, n);
}, zn = [], Ye = Ui(), Di = pr(Ye), Hn = ir(Di), Wi = xi(Hn, lr, dr, et), Mt = _r(qn), Vi = wr(Mt), Fi = vr(Mt), ji = ar(Vi, Fi), $i = Pi(Hn, ji, Mt), Gi = ur(Ye), qi = mr(Ye), sa = hr(gr(et), et, Wi, $i, zn, cr(Gi, Bi), qi), ia = () => fr(Ye), aa = async (e) => {
  zn.push(await sr(e));
};
export {
  sa as MediaRecorder,
  ia as isSupported,
  aa as register
};
