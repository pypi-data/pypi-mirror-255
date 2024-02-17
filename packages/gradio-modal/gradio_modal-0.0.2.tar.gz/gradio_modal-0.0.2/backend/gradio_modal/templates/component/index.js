const {
  SvelteComponent: R,
  assign: V,
  create_slot: W,
  detach: X,
  element: Y,
  get_all_dirty_from_scope: Z,
  get_slot_changes: p,
  get_spread_update: x,
  init: $,
  insert: ee,
  safe_not_equal: le,
  set_dynamic_element_data: z,
  set_style: m,
  toggle_class: g,
  transition_in: U,
  transition_out: F,
  update_slot_base: te
} = window.__gradio__svelte__internal;
function fe(f) {
  let e, l, a;
  const n = (
    /*#slots*/
    f[18].default
  ), i = W(
    n,
    f,
    /*$$scope*/
    f[17],
    null
  );
  let d = [
    { "data-testid": (
      /*test_id*/
      f[7]
    ) },
    { id: (
      /*elem_id*/
      f[2]
    ) },
    {
      class: l = "block " + /*elem_classes*/
      f[3].join(" ") + " svelte-1t38q2d"
    }
  ], s = {};
  for (let t = 0; t < d.length; t += 1)
    s = V(s, d[t]);
  return {
    c() {
      e = Y(
        /*tag*/
        f[14]
      ), i && i.c(), z(
        /*tag*/
        f[14]
      )(e, s), g(
        e,
        "hidden",
        /*visible*/
        f[10] === !1
      ), g(
        e,
        "padded",
        /*padding*/
        f[6]
      ), g(
        e,
        "border_focus",
        /*border_mode*/
        f[5] === "focus"
      ), g(e, "hide-container", !/*explicit_call*/
      f[8] && !/*container*/
      f[9]), m(
        e,
        "height",
        /*get_dimension*/
        f[15](
          /*height*/
          f[0]
        )
      ), m(e, "width", typeof /*width*/
      f[1] == "number" ? `calc(min(${/*width*/
      f[1]}px, 100%))` : (
        /*get_dimension*/
        f[15](
          /*width*/
          f[1]
        )
      )), m(
        e,
        "border-style",
        /*variant*/
        f[4]
      ), m(
        e,
        "overflow",
        /*allow_overflow*/
        f[11] ? "visible" : "hidden"
      ), m(
        e,
        "flex-grow",
        /*scale*/
        f[12]
      ), m(e, "min-width", `calc(min(${/*min_width*/
      f[13]}px, 100%))`), m(e, "border-width", "var(--block-border-width)");
    },
    m(t, o) {
      ee(t, e, o), i && i.m(e, null), a = !0;
    },
    p(t, o) {
      i && i.p && (!a || o & /*$$scope*/
      131072) && te(
        i,
        n,
        t,
        /*$$scope*/
        t[17],
        a ? p(
          n,
          /*$$scope*/
          t[17],
          o,
          null
        ) : Z(
          /*$$scope*/
          t[17]
        ),
        null
      ), z(
        /*tag*/
        t[14]
      )(e, s = x(d, [
        (!a || o & /*test_id*/
        128) && { "data-testid": (
          /*test_id*/
          t[7]
        ) },
        (!a || o & /*elem_id*/
        4) && { id: (
          /*elem_id*/
          t[2]
        ) },
        (!a || o & /*elem_classes*/
        8 && l !== (l = "block " + /*elem_classes*/
        t[3].join(" ") + " svelte-1t38q2d")) && { class: l }
      ])), g(
        e,
        "hidden",
        /*visible*/
        t[10] === !1
      ), g(
        e,
        "padded",
        /*padding*/
        t[6]
      ), g(
        e,
        "border_focus",
        /*border_mode*/
        t[5] === "focus"
      ), g(e, "hide-container", !/*explicit_call*/
      t[8] && !/*container*/
      t[9]), o & /*height*/
      1 && m(
        e,
        "height",
        /*get_dimension*/
        t[15](
          /*height*/
          t[0]
        )
      ), o & /*width*/
      2 && m(e, "width", typeof /*width*/
      t[1] == "number" ? `calc(min(${/*width*/
      t[1]}px, 100%))` : (
        /*get_dimension*/
        t[15](
          /*width*/
          t[1]
        )
      )), o & /*variant*/
      16 && m(
        e,
        "border-style",
        /*variant*/
        t[4]
      ), o & /*allow_overflow*/
      2048 && m(
        e,
        "overflow",
        /*allow_overflow*/
        t[11] ? "visible" : "hidden"
      ), o & /*scale*/
      4096 && m(
        e,
        "flex-grow",
        /*scale*/
        t[12]
      ), o & /*min_width*/
      8192 && m(e, "min-width", `calc(min(${/*min_width*/
      t[13]}px, 100%))`);
    },
    i(t) {
      a || (U(i, t), a = !0);
    },
    o(t) {
      F(i, t), a = !1;
    },
    d(t) {
      t && X(e), i && i.d(t);
    }
  };
}
function ne(f) {
  let e, l = (
    /*tag*/
    f[14] && fe(f)
  );
  return {
    c() {
      l && l.c();
    },
    m(a, n) {
      l && l.m(a, n), e = !0;
    },
    p(a, [n]) {
      /*tag*/
      a[14] && l.p(a, n);
    },
    i(a) {
      e || (U(l, a), e = !0);
    },
    o(a) {
      F(l, a), e = !1;
    },
    d(a) {
      l && l.d(a);
    }
  };
}
function ae(f, e, l) {
  let { $$slots: a = {}, $$scope: n } = e, { height: i = void 0 } = e, { width: d = void 0 } = e, { elem_id: s = "" } = e, { elem_classes: t = [] } = e, { variant: o = "solid" } = e, { border_mode: u = "base" } = e, { padding: b = !0 } = e, { type: c = "normal" } = e, { test_id: w = void 0 } = e, { explicit_call: r = !1 } = e, { container: B = !0 } = e, { visible: L = !0 } = e, { allow_overflow: T = !0 } = e, { scale: E = null } = e, { min_width: M = 0 } = e, P = c === "fieldset" ? "fieldset" : "div";
  const Q = (_) => {
    if (_ !== void 0) {
      if (typeof _ == "number")
        return _ + "px";
      if (typeof _ == "string")
        return _;
    }
  };
  return f.$$set = (_) => {
    "height" in _ && l(0, i = _.height), "width" in _ && l(1, d = _.width), "elem_id" in _ && l(2, s = _.elem_id), "elem_classes" in _ && l(3, t = _.elem_classes), "variant" in _ && l(4, o = _.variant), "border_mode" in _ && l(5, u = _.border_mode), "padding" in _ && l(6, b = _.padding), "type" in _ && l(16, c = _.type), "test_id" in _ && l(7, w = _.test_id), "explicit_call" in _ && l(8, r = _.explicit_call), "container" in _ && l(9, B = _.container), "visible" in _ && l(10, L = _.visible), "allow_overflow" in _ && l(11, T = _.allow_overflow), "scale" in _ && l(12, E = _.scale), "min_width" in _ && l(13, M = _.min_width), "$$scope" in _ && l(17, n = _.$$scope);
  }, [
    i,
    d,
    s,
    t,
    o,
    u,
    b,
    w,
    r,
    B,
    L,
    T,
    E,
    M,
    P,
    Q,
    c,
    n,
    a
  ];
}
class ie extends R {
  constructor(e) {
    super(), $(this, e, ae, ne, le, {
      height: 0,
      width: 1,
      elem_id: 2,
      elem_classes: 3,
      variant: 4,
      border_mode: 5,
      padding: 6,
      type: 16,
      test_id: 7,
      explicit_call: 8,
      container: 9,
      visible: 10,
      allow_overflow: 11,
      scale: 12,
      min_width: 13
    });
  }
}
const se = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], A = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
se.reduce(
  (f, { color: e, primary: l, secondary: a }) => ({
    ...f,
    [e]: {
      primary: A[e][l],
      secondary: A[e][a]
    }
  }),
  {}
);
const {
  SvelteComponent: _e,
  attr: y,
  create_slot: de,
  detach: oe,
  element: ce,
  get_all_dirty_from_scope: re,
  get_slot_changes: ue,
  init: me,
  insert: be,
  null_to_empty: D,
  safe_not_equal: ge,
  set_style: k,
  toggle_class: h,
  transition_in: he,
  transition_out: ve,
  update_slot_base: we
} = window.__gradio__svelte__internal;
function ye(f) {
  let e, l, a = `calc(min(${/*min_width*/
  f[2]}px, 100%))`, n;
  const i = (
    /*#slots*/
    f[8].default
  ), d = de(
    i,
    f,
    /*$$scope*/
    f[7],
    null
  );
  return {
    c() {
      e = ce("div"), d && d.c(), y(
        e,
        "id",
        /*elem_id*/
        f[3]
      ), y(e, "class", l = D(
        /*elem_classes*/
        f[4].join(" ")
      ) + " svelte-1m1obck"), h(
        e,
        "gap",
        /*gap*/
        f[1]
      ), h(
        e,
        "compact",
        /*variant*/
        f[6] === "compact"
      ), h(
        e,
        "panel",
        /*variant*/
        f[6] === "panel"
      ), h(e, "hide", !/*visible*/
      f[5]), k(
        e,
        "flex-grow",
        /*scale*/
        f[0]
      ), k(e, "min-width", a);
    },
    m(s, t) {
      be(s, e, t), d && d.m(e, null), n = !0;
    },
    p(s, [t]) {
      d && d.p && (!n || t & /*$$scope*/
      128) && we(
        d,
        i,
        s,
        /*$$scope*/
        s[7],
        n ? ue(
          i,
          /*$$scope*/
          s[7],
          t,
          null
        ) : re(
          /*$$scope*/
          s[7]
        ),
        null
      ), (!n || t & /*elem_id*/
      8) && y(
        e,
        "id",
        /*elem_id*/
        s[3]
      ), (!n || t & /*elem_classes*/
      16 && l !== (l = D(
        /*elem_classes*/
        s[4].join(" ")
      ) + " svelte-1m1obck")) && y(e, "class", l), (!n || t & /*elem_classes, gap*/
      18) && h(
        e,
        "gap",
        /*gap*/
        s[1]
      ), (!n || t & /*elem_classes, variant*/
      80) && h(
        e,
        "compact",
        /*variant*/
        s[6] === "compact"
      ), (!n || t & /*elem_classes, variant*/
      80) && h(
        e,
        "panel",
        /*variant*/
        s[6] === "panel"
      ), (!n || t & /*elem_classes, visible*/
      48) && h(e, "hide", !/*visible*/
      s[5]), t & /*scale*/
      1 && k(
        e,
        "flex-grow",
        /*scale*/
        s[0]
      ), t & /*min_width*/
      4 && a !== (a = `calc(min(${/*min_width*/
      s[2]}px, 100%))`) && k(e, "min-width", a);
    },
    i(s) {
      n || (he(d, s), n = !0);
    },
    o(s) {
      ve(d, s), n = !1;
    },
    d(s) {
      s && oe(e), d && d.d(s);
    }
  };
}
function ke(f, e, l) {
  let { $$slots: a = {}, $$scope: n } = e, { scale: i = null } = e, { gap: d = !0 } = e, { min_width: s = 0 } = e, { elem_id: t = "" } = e, { elem_classes: o = [] } = e, { visible: u = !0 } = e, { variant: b = "default" } = e;
  return f.$$set = (c) => {
    "scale" in c && l(0, i = c.scale), "gap" in c && l(1, d = c.gap), "min_width" in c && l(2, s = c.min_width), "elem_id" in c && l(3, t = c.elem_id), "elem_classes" in c && l(4, o = c.elem_classes), "visible" in c && l(5, u = c.visible), "variant" in c && l(6, b = c.variant), "$$scope" in c && l(7, n = c.$$scope);
  }, [i, d, s, t, o, u, b, n, a];
}
let je = class extends _e {
  constructor(e) {
    super(), me(this, e, ke, ye, ge, {
      scale: 0,
      gap: 1,
      min_width: 2,
      elem_id: 3,
      elem_classes: 4,
      visible: 5,
      variant: 6
    });
  }
};
const {
  SvelteComponent: Ce,
  append: qe,
  attr: v,
  binding_callbacks: Ie,
  create_component: G,
  create_slot: Se,
  destroy_component: J,
  detach: C,
  element: j,
  get_all_dirty_from_scope: Be,
  get_slot_changes: Le,
  init: Te,
  insert: q,
  listen: K,
  mount_component: O,
  noop: Ee,
  safe_not_equal: Me,
  space: ze,
  toggle_class: H,
  transition_in: I,
  transition_out: S,
  update_slot_base: Ae
} = window.__gradio__svelte__internal;
function N(f) {
  let e, l, a;
  return {
    c() {
      e = j("div"), e.innerHTML = '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1 1L9 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9 1L1 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>', v(e, "class", "close svelte-ra5mg6");
    },
    m(n, i) {
      q(n, e, i), l || (a = K(
        e,
        "click",
        /*close*/
        f[5]
      ), l = !0);
    },
    p: Ee,
    d(n) {
      n && C(e), l = !1, a();
    }
  };
}
function De(f) {
  let e;
  const l = (
    /*#slots*/
    f[7].default
  ), a = Se(
    l,
    f,
    /*$$scope*/
    f[10],
    null
  );
  return {
    c() {
      a && a.c();
    },
    m(n, i) {
      a && a.m(n, i), e = !0;
    },
    p(n, i) {
      a && a.p && (!e || i & /*$$scope*/
      1024) && Ae(
        a,
        l,
        n,
        /*$$scope*/
        n[10],
        e ? Le(
          l,
          /*$$scope*/
          n[10],
          i,
          null
        ) : Be(
          /*$$scope*/
          n[10]
        ),
        null
      );
    },
    i(n) {
      e || (I(a, n), e = !0);
    },
    o(n) {
      S(a, n), e = !1;
    },
    d(n) {
      a && a.d(n);
    }
  };
}
function He(f) {
  let e, l, a, n = (
    /*allow_user_close*/
    f[3] && N(f)
  );
  return l = new je({
    props: {
      $$slots: { default: [De] },
      $$scope: { ctx: f }
    }
  }), {
    c() {
      n && n.c(), e = ze(), G(l.$$.fragment);
    },
    m(i, d) {
      n && n.m(i, d), q(i, e, d), O(l, i, d), a = !0;
    },
    p(i, d) {
      /*allow_user_close*/
      i[3] ? n ? n.p(i, d) : (n = N(i), n.c(), n.m(e.parentNode, e)) : n && (n.d(1), n = null);
      const s = {};
      d & /*$$scope*/
      1024 && (s.$$scope = { dirty: d, ctx: i }), l.$set(s);
    },
    i(i) {
      a || (I(l.$$.fragment, i), a = !0);
    },
    o(i) {
      S(l.$$.fragment, i), a = !1;
    },
    d(i) {
      i && C(e), n && n.d(i), J(l, i);
    }
  };
}
function Ne(f) {
  let e, l, a, n, i, d, s;
  return a = new ie({
    props: {
      height: "100%",
      $$slots: { default: [He] },
      $$scope: { ctx: f }
    }
  }), {
    c() {
      e = j("div"), l = j("div"), G(a.$$.fragment), v(l, "class", "modal-container svelte-ra5mg6"), v(e, "class", n = "modal " + /*elem_classes*/
      f[2].join(" ") + " svelte-ra5mg6"), v(
        e,
        "id",
        /*elem_id*/
        f[1]
      ), H(e, "hide", !/*visible*/
      f[0]);
    },
    m(t, o) {
      q(t, e, o), qe(e, l), O(a, l, null), f[8](e), i = !0, d || (s = K(
        e,
        "click",
        /*click_handler*/
        f[9]
      ), d = !0);
    },
    p(t, [o]) {
      const u = {};
      o & /*$$scope, allow_user_close*/
      1032 && (u.$$scope = { dirty: o, ctx: t }), a.$set(u), (!i || o & /*elem_classes*/
      4 && n !== (n = "modal " + /*elem_classes*/
      t[2].join(" ") + " svelte-ra5mg6")) && v(e, "class", n), (!i || o & /*elem_id*/
      2) && v(
        e,
        "id",
        /*elem_id*/
        t[1]
      ), (!i || o & /*elem_classes, visible*/
      5) && H(e, "hide", !/*visible*/
      t[0]);
    },
    i(t) {
      i || (I(a.$$.fragment, t), i = !0);
    },
    o(t) {
      S(a.$$.fragment, t), i = !1;
    },
    d(t) {
      t && C(e), J(a), f[8](null), d = !1, s();
    }
  };
}
function Ue(f, e, l) {
  let { $$slots: a = {}, $$scope: n } = e, { elem_id: i = "" } = e, { elem_classes: d = [] } = e, { visible: s = !1 } = e, { allow_user_close: t = !0 } = e, { gradio: o } = e, u = null;
  const b = () => {
    l(0, s = !1), o.dispatch("blur");
  };
  document.addEventListener("keydown", (r) => {
    t && r.key === "Escape" && b();
  });
  function c(r) {
    Ie[r ? "unshift" : "push"](() => {
      u = r, l(4, u);
    });
  }
  const w = (r) => {
    t && r.target === u && b();
  };
  return f.$$set = (r) => {
    "elem_id" in r && l(1, i = r.elem_id), "elem_classes" in r && l(2, d = r.elem_classes), "visible" in r && l(0, s = r.visible), "allow_user_close" in r && l(3, t = r.allow_user_close), "gradio" in r && l(6, o = r.gradio), "$$scope" in r && l(10, n = r.$$scope);
  }, [
    s,
    i,
    d,
    t,
    u,
    b,
    o,
    a,
    c,
    w,
    n
  ];
}
class Ge extends Ce {
  constructor(e) {
    super(), Te(this, e, Ue, Ne, Me, {
      elem_id: 1,
      elem_classes: 2,
      visible: 0,
      allow_user_close: 3,
      gradio: 6
    });
  }
}
export {
  Ge as default
};
