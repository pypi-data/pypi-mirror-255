const {
  SvelteComponent: A,
  append: k,
  attr: f,
  detach: B,
  init: D,
  insert: F,
  noop: h,
  safe_not_equal: H,
  svg_element: w
} = window.__gradio__svelte__internal;
function P(s) {
  let e, i, a;
  return {
    c() {
      e = w("svg"), i = w("path"), a = w("polyline"), f(i, "d", "M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"), f(a, "points", "13 2 13 9 20 9"), f(e, "xmlns", "http://www.w3.org/2000/svg"), f(e, "width", "100%"), f(e, "height", "100%"), f(e, "viewBox", "0 0 24 24"), f(e, "fill", "none"), f(e, "stroke", "currentColor"), f(e, "stroke-width", "1.5"), f(e, "stroke-linecap", "round"), f(e, "stroke-linejoin", "round"), f(e, "class", "feather feather-file");
    },
    m(r, _) {
      F(r, e, _), k(e, i), k(e, a);
    },
    p: h,
    i: h,
    o: h,
    d(r) {
      r && B(e);
    }
  };
}
class V extends A {
  constructor(e) {
    super(), D(this, e, null, P, H, {});
  }
}
const {
  SvelteComponent: W,
  add_iframe_resize_listener: G,
  add_render_callback: I,
  append: g,
  attr: y,
  binding_callbacks: J,
  check_outros: K,
  create_component: L,
  destroy_component: N,
  detach: C,
  element: v,
  group_outros: O,
  init: Q,
  insert: S,
  mount_component: R,
  safe_not_equal: T,
  set_data: q,
  space: E,
  text: M,
  toggle_class: p,
  transition_in: m,
  transition_out: b
} = window.__gradio__svelte__internal, { onMount: U } = window.__gradio__svelte__internal;
function j(s) {
  let e, i, a, r, _ = (
    /*value*/
    s[0].files.map(z).join(", ") + ""
  ), u, l;
  return a = new V({}), {
    c() {
      e = v("span"), i = v("i"), L(a.$$.fragment), r = E(), u = M(_), y(i, "class", "svelte-1j28ovu"), y(e, "class", "files svelte-1j28ovu");
    },
    m(t, c) {
      S(t, e, c), g(e, i), R(a, i, null), g(e, r), g(e, u), l = !0;
    },
    p(t, c) {
      (!l || c & /*value*/
      1) && _ !== (_ = /*value*/
      t[0].files.map(z).join(", ") + "") && q(u, _);
    },
    i(t) {
      l || (m(a.$$.fragment, t), l = !0);
    },
    o(t) {
      b(a.$$.fragment, t), l = !1;
    },
    d(t) {
      t && C(e), N(a);
    }
  };
}
function X(s) {
  var c;
  let e, i, a = (
    /*value*/
    s[0].text + ""
  ), r, _, u, l, t = (
    /*value*/
    ((c = s[0].files) == null ? void 0 : c.length) > 0 && j(s)
  );
  return {
    c() {
      e = v("div"), i = v("span"), r = M(a), _ = E(), t && t.c(), y(e, "class", "svelte-1j28ovu"), I(() => (
        /*div_elementresize_handler*/
        s[5].call(e)
      )), p(
        e,
        "table",
        /*type*/
        s[1] === "table"
      ), p(
        e,
        "gallery",
        /*type*/
        s[1] === "gallery"
      ), p(
        e,
        "selected",
        /*selected*/
        s[2]
      );
    },
    m(o, n) {
      S(o, e, n), g(e, i), g(i, r), g(e, _), t && t.m(e, null), u = G(
        e,
        /*div_elementresize_handler*/
        s[5].bind(e)
      ), s[6](e), l = !0;
    },
    p(o, [n]) {
      var d;
      (!l || n & /*value*/
      1) && a !== (a = /*value*/
      o[0].text + "") && q(r, a), /*value*/
      ((d = o[0].files) == null ? void 0 : d.length) > 0 ? t ? (t.p(o, n), n & /*value*/
      1 && m(t, 1)) : (t = j(o), t.c(), m(t, 1), t.m(e, null)) : t && (O(), b(t, 1, 1, () => {
        t = null;
      }), K()), (!l || n & /*type*/
      2) && p(
        e,
        "table",
        /*type*/
        o[1] === "table"
      ), (!l || n & /*type*/
      2) && p(
        e,
        "gallery",
        /*type*/
        o[1] === "gallery"
      ), (!l || n & /*selected*/
      4) && p(
        e,
        "selected",
        /*selected*/
        o[2]
      );
    },
    i(o) {
      l || (m(t), l = !0);
    },
    o(o) {
      b(t), l = !1;
    },
    d(o) {
      o && C(e), t && t.d(), u(), s[6](null);
    }
  };
}
const z = (s) => s.orig_name;
function Y(s, e, i) {
  let { value: a } = e, { type: r } = e, { selected: _ = !1 } = e, u, l;
  function t(n, d) {
    !n || !d || (l.style.setProperty("--local-text-width", `${d < 150 ? d : 200}px`), i(4, l.style.whiteSpace = "unset", l));
  }
  U(() => {
    t(l, u);
  });
  function c() {
    u = this.clientWidth, i(3, u);
  }
  function o(n) {
    J[n ? "unshift" : "push"](() => {
      l = n, i(4, l);
    });
  }
  return s.$$set = (n) => {
    "value" in n && i(0, a = n.value), "type" in n && i(1, r = n.type), "selected" in n && i(2, _ = n.selected);
  }, [a, r, _, u, l, c, o];
}
class Z extends W {
  constructor(e) {
    super(), Q(this, e, Y, X, T, { value: 0, type: 1, selected: 2 });
  }
}
export {
  Z as default
};
