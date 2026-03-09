"""Sidebar component — Tailwind + DashIconify."""

from dash import html, dcc
from dash_iconify import DashIconify


def _icon(name, size=20, cls=""):
    """Shortcut to create a DashIconify element."""
    return DashIconify(icon=name, width=size, className=cls)


def _nav_link(icon_name, label, href):
    return dcc.Link(
        className=(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg text-txtsec text-sm "
            "hover:bg-neonsoft hover:text-neon transition-all duration-200 nav-link"
        ),
        href=href,
        children=[
            _icon(icon_name, 20, "shrink-0"),
            html.Span(label),
        ],
    )


def create_sidebar():
    return html.Div(
        className=(
            "w-[280px] min-w-[280px] fixed top-0 left-0 h-screen overflow-y-auto "
            "flex flex-col bg-sidebar border-r border-neonbrd/30 px-4 py-6 z-50 "
            "transition-colors duration-300"
        ),
        children=[
            # ── Logo ──
            html.Div(className="flex items-center gap-3 px-3 mb-7", children=[
                _icon("lucide:heart-pulse", 30, "text-neon drop-shadow-[0_0_8px_rgba(0,212,255,0.5)]"),
                html.Div([
                    html.H2("CardioViz",
                            className="text-xl font-extrabold text-neon tracking-tight "
                                      "drop-shadow-[0_0_12px_rgba(0,212,255,0.35)]"),
                    html.Div("Heart Disease Dashboard",
                             className="text-[11px] text-txtsec uppercase tracking-widest"),
                ]),
            ]),

            # ── Navigation ──
            html.Div(className="mb-6 space-y-0.5", children=[
                html.Div("Trang phân tích",
                         className="text-[11px] font-semibold text-txtsec uppercase tracking-wider px-3 mb-2"),
                _nav_link("lucide:database",          "Khám Phá Dữ Liệu", "/eda"),
                _nav_link("lucide:layout-dashboard",  "Tổng Quan KPI", "/"),
                _nav_link("lucide:trending-up",       "Xu Hướng Tuổi", "/age-trends"),
                _nav_link("lucide:microscope",        "Lâm Sàng Chuyên Sâu", "/clinical-deep-dive"),
                _nav_link("lucide:scatter-chart",     "Tương Quan Đa Biến", "/correlation"),
                _nav_link("lucide:shield-alert",      "Cảnh Báo & Khuyến Nghị", "/alerts"),
            ]),

            # ── Divider ──
            html.Hr(className="border-neonbrd/30 my-2"),

            # ── Global Filters ──
            html.Div(className="space-y-4 mt-2", children=[
                html.Div("Bộ lọc toàn cục",
                         className="text-[11px] font-semibold text-txtsec uppercase tracking-wider px-3"),

                # Sex
                html.Div(className="px-2", children=[
                    html.Label([
                        _icon("lucide:users", 14, "inline mr-1 text-txtsec"),
                        "Giới tính",
                    ], className="text-xs font-medium text-txtsec mb-1.5 block"),
                    dcc.Dropdown(
                        id="filter-sex",
                        options=[
                            {"label": "Tất cả", "value": "all"},
                            {"label": "Nam giới", "value": 1},
                            {"label": "Nữ giới", "value": 0},
                        ],
                        value="all", clearable=False,
                    ),
                ]),

                # Age
                html.Div(className="px-2", children=[
                    html.Label([
                        _icon("lucide:calendar-days", 14, "inline mr-1 text-txtsec"),
                        "Khoảng tuổi",
                    ], className="text-xs font-medium text-txtsec mb-1.5 block"),
                    dcc.RangeSlider(
                        id="filter-age", min=20, max=80, step=1, value=[20, 80],
                        marks={20: "20", 30: "30", 40: "40", 50: "50",
                               60: "60", 70: "70", 80: "80"},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ]),

                # Chest pain
                html.Div(className="px-2", children=[
                    html.Label([
                        _icon("lucide:stethoscope", 14, "inline mr-1 text-txtsec"),
                        "Loại đau ngực",
                    ], className="text-xs font-medium text-txtsec mb-1.5 block"),
                    dcc.Dropdown(
                        id="filter-cp",
                        options=[
                            {"label": "Tất cả", "value": "all"},
                            {"label": "Đau thắt ngực điển hình", "value": 1},
                            {"label": "Đau không điển hình", "value": 2},
                            {"label": "Đau không do mạch vành", "value": 3},
                            {"label": "Không triệu chứng", "value": 0},
                        ],
                        value="all", clearable=False,
                    ),
                ]),

                # Target
                html.Div(className="px-2", children=[
                    html.Label([
                        _icon("lucide:activity", 14, "inline mr-1 text-txtsec"),
                        "Chẩn đoán (target)",
                    ], className="text-xs font-medium text-txtsec mb-1.5 block"),
                    dcc.Dropdown(
                        id="filter-target",
                        options=[
                            {"label": "Tất cả", "value": "all"},
                            {"label": "Có bệnh tim", "value": 1},
                            {"label": "Không bệnh tim", "value": 0},
                        ],
                        value="all", clearable=False,
                    ),
                ]),
            ]),

            # ── Spacer ──
            html.Div(className="flex-1"),

            # ── Theme toggle ──
            html.Button(
                id="theme-toggle-btn",
                className=(
                    "flex items-center gap-2.5 w-full px-3 py-2.5 mt-4 rounded-lg "
                    "border border-neonbrd/30 bg-inputbg text-txtsec text-sm cursor-pointer "
                    "hover:bg-neonsoft hover:text-neon hover:border-neonbrd "
                    "hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] "
                    "transition-all duration-200"
                ),
                children=[
                    DashIconify(icon="lucide:moon", width=18),
                    "Dark Mode",
                ],
                n_clicks=0,
            ),
        ],
    )
