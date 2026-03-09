"""Page 5 — Cảnh Báo & Chẩn Đoán Cá Nhân (Patient Risk Alerts)"""
import dash, numpy as np
from dash import html, dcc, callback, Input, Output, State
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from components.theme import get_theme

dash.register_page(__name__, path="/alerts", name="Cảnh Báo Sức Khỏe", order=4)

I = lambda name, sz=20, cls="": DashIconify(icon=name, width=sz, className=cls)

# ── Thresholds & helpers ──
THRESHOLDS = {
    "chol": 200, "trestbps": 130, "thalach": 140,
    "oldpeak": 1.5, "fbs": 1, "exang": 1, "ca": 0,
}

WARNING = "warning"
DANGER  = "danger"
SUCCESS = "success"


def _compute_risk_factors(row):
    """Returns list of (factor_name, icon, severity_class, detail)."""
    factors = []
    if row["chol"] > THRESHOLDS["chol"]:
        factors.append(("Cholesterol cao", "lucide:droplets", DANGER,
                        f'{row["chol"]} mg/dl (ngưỡng {THRESHOLDS["chol"]})'))
    if row["trestbps"] > THRESHOLDS["trestbps"]:
        factors.append(("Huyết áp cao", "lucide:gauge", DANGER,
                        f'{row["trestbps"]} mmHg (ngưỡng {THRESHOLDS["trestbps"]})'))
    if row["thalach"] < THRESHOLDS["thalach"]:
        factors.append(("Nhịp tim thấp", "lucide:heart-pulse", WARNING,
                        f'{row["thalach"]} bpm (ngưỡng {THRESHOLDS["thalach"]})'))
    if row["oldpeak"] > THRESHOLDS["oldpeak"]:
        factors.append(("ST chênh cao", "lucide:activity", DANGER,
                        f'{row["oldpeak"]} (ngưỡng {THRESHOLDS["oldpeak"]})'))
    if row["fbs"] == THRESHOLDS["fbs"]:
        factors.append(("Đường huyết cao", "lucide:candy", WARNING,
                        "FBS > 120 mg/dl"))
    if row["exang"] == THRESHOLDS["exang"]:
        factors.append(("Đau khi vận động", "lucide:zap", WARNING,
                        "Có triệu chứng exang"))
    if row["ca"] > THRESHOLDS["ca"]:
        factors.append(("Mạch tắc nghẽn", "lucide:git-branch", DANGER,
                        f'{int(row["ca"])} mạch bị tắc'))
    if row["cp"] == 0:
        factors.append(("Thiếu máu thầm lặng", "lucide:shield-alert", WARNING,
                        "Không có triệu chứng đau ngực (cp=0)"))
    return factors


def _risk_level(total_score):
    if total_score <= 2:
        return SUCCESS, "Nguy Cơ Thấp", "#27ae60"
    elif total_score <= 4:
        return WARNING, "Nguy Cơ Trung Bình", "#f39c12"
    else:
        return DANGER, "Nguy Cơ Cao", "#e74c3c"


def _kpi_mini(icon, label, value, cls_ring="ring-neonbrd"):
    return html.Div(
        className=f"bg-card border border-neonbrd/30 rounded-lg p-3 text-center ring-1 {cls_ring}",
        children=[
            I(icon, 22, "text-neon mx-auto mb-1"),
            html.P(label, className="text-[10px] text-txtsec uppercase tracking-wide"),
            html.P(value, className="text-lg font-bold text-txtpri"),
        ],
    )


# ── Layout ──
layout = html.Div([
    html.Div(className="mb-7", children=[
        html.Div(className="flex items-center gap-3 mb-1", children=[
            I("lucide:shield-alert", 28, "text-neon"),
            html.H1("Cảnh Báo & Chẩn Đoán Cá Nhân",
                     className="text-2xl font-extrabold text-txtpri tracking-tight"),
        ]),
        html.P("Patient Risk Alerts — Phân tích yếu tố nguy cơ cho từng bệnh nhân",
               className="text-sm text-txtsec"),
    ]),
    # Patient selector
    html.Div(
        className=(
            "bg-card border border-neonbrd/30 rounded-xl p-5 mb-5 "
            "flex flex-wrap items-end gap-4"
        ),
        children=[
            html.Div(className="flex-1 min-w-[200px]", children=[
                html.Label([I("lucide:user-search", 16, "mr-1.5"), "Chọn bệnh nhân (index)"],
                           className="text-xs font-medium text-txtsec mb-1 flex items-center"),
                dcc.Input(id="patient-idx", type="number", min=0, value=0,
                          className=(
                              "w-full bg-inputbg border border-neonbrd/30 rounded-lg "
                              "px-3 py-2 text-txtpri text-sm focus:outline-none "
                              "focus:ring-2 focus:ring-neon/40"
                          )),
            ]),
            html.Button(
                [I("lucide:search", 16, "mr-1.5"), "Phân Tích"],
                id="btn-analyze",
                className=(
                    "px-5 py-2.5 rounded-lg bg-neon/20 text-neon text-sm font-semibold "
                    "border border-neon/40 hover:bg-neon/30 transition-colors "
                    "flex items-center gap-1"
                ),
            ),
        ],
    ),
    html.Div(id="alert-result"),
])


# ── Callback ──
@callback(
    Output("alert-result", "children"),
    Input("btn-analyze", "n_clicks"),
    [State("filtered-data-store", "data"),
     State("patient-idx", "value"),
     State("theme-store", "data")],
    prevent_initial_call=True,
)
def analyze_patient(n_clicks, json_data, idx, theme):
    T = get_theme(theme)
    if json_data is None:
        return html.P("Không có dữ liệu.", className="text-txtsec")
    dff = pd.read_json(StringIO(json_data), orient="split")
    if idx is None or idx < 0 or idx >= len(dff):
        return html.P(f"Index không hợp lệ. Phạm vi: 0 – {len(dff)-1}",
                       className="text-danger")

    row = dff.iloc[idx]
    factors = _compute_risk_factors(row)
    sev_cls, sev_label, sev_color = _risk_level(len(factors))

    sex_label = "Nam" if row["sex"] == 1 else "Nữ"
    cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
              2: "Đau không điển hình", 3: "Không do mạch vành"}

    # ── Build output sections ──
    kpi_row = html.Div(
        className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 mb-5",
        children=[
            _kpi_mini("lucide:user", "Giới tính", sex_label),
            _kpi_mini("lucide:calendar-days", "Tuổi", str(int(row["age"]))),
            _kpi_mini("lucide:stethoscope", "Đau ngực", cp_map.get(row["cp"], "?")),
            _kpi_mini("lucide:gauge", "Huyết áp", f'{int(row["trestbps"])}'),
            _kpi_mini("lucide:droplets", "Chol", f'{int(row["chol"])}'),
            _kpi_mini("lucide:heart-pulse", "Nhịp max", f'{int(row["thalach"])}'),
            _kpi_mini("lucide:activity", "Oldpeak", f'{row["oldpeak"]:.1f}'),
            _kpi_mini("lucide:git-branch", "CA", f'{int(row["ca"])}'),
        ],
    )

    # Risk badge
    badge = html.Div(
        className="flex items-center gap-3 mb-5",
        children=[
            html.Div(
                className=f"px-4 py-2 rounded-full border text-sm font-bold",
                style={"borderColor": sev_color, "color": sev_color,
                       "backgroundColor": sev_color + "18"},
                children=[I("lucide:alert-triangle", 16, "mr-1.5 inline-block"), sev_label],
            ),
            html.Span(f"{len(factors)} yếu tố nguy cơ phát hiện",
                       className="text-sm text-txtsec"),
        ],
    )

    # Waterfall chart
    wf_names = [f[0] for f in factors] + ["Tổng"]
    wf_values = [1] * len(factors) + [len(factors)]
    wf_measures = ["relative"] * len(factors) + ["total"]
    wf_colors = []
    for f in factors:
        wf_colors.append(T["danger"] if f[2] == DANGER else T["warning"])
    wf_colors.append(sev_color)

    waterfall_fig = go.Figure(go.Waterfall(
        x=wf_names, y=wf_values, measure=wf_measures,
        connector_line_color="rgba(0,0,0,0)",
        increasing_marker_color=T["danger"],
        totals_marker_color=sev_color,
        textposition="outside", text=["+1"] * len(factors) + [str(len(factors))],
    ))
    waterfall_fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        margin=dict(t=20, b=60, l=40, r=20), height=300,
        xaxis_tickangle=-30, yaxis_title="Điểm tích lũy",
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )

    waterfall_card = html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:bar-chart-3", 18, "text-neon"),
                html.H3("Waterfall — Tích Lũy Nguy Cơ", className="text-sm font-semibold text-txtpri"),
            ]),
            dcc.Graph(figure=waterfall_fig, config={"displayModeBar": False}),
        ],
    )

    # Factor table
    if factors:
        table_rows = []
        for fname, ficon, fsev, fdetail in factors:
            sev_cls_map = {DANGER: "text-danger", WARNING: "text-warning", SUCCESS: "text-success"}
            sev_lbl_map = {DANGER: "Cao", WARNING: "TB", SUCCESS: "Thấp"}
            table_rows.append(
                html.Tr(className="border-b border-neonbrd/20", children=[
                    html.Td(I(ficon, 18, sev_cls_map.get(fsev, "text-txtsec")),
                            className="py-2.5 pr-2"),
                    html.Td(fname, className="py-2.5 text-sm text-txtpri font-medium"),
                    html.Td(
                        html.Span(sev_lbl_map.get(fsev, "?"),
                                  className=f"text-[11px] font-bold px-2 py-0.5 rounded-full "
                                            f"{sev_cls_map.get(fsev, '')} "
                                            f"bg-{fsev}/10 border border-{fsev}/30"),
                        className="py-2.5"),
                    html.Td(fdetail, className="py-2.5 text-xs text-txtsec"),
                ])
            )
        factor_table = html.Div(
            className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5 overflow-x-auto",
            children=[
                html.Div(className="flex items-center gap-2 mb-3", children=[
                    I("lucide:list-checks", 18, "text-neon"),
                    html.H3("Chi Tiết Yếu Tố Nguy Cơ", className="text-sm font-semibold text-txtpri"),
                ]),
                html.Table(className="w-full", children=[
                    html.Thead(html.Tr([
                        html.Th("", className="pb-2 text-left text-[10px] text-txtsec uppercase"),
                        html.Th("Yếu tố", className="pb-2 text-left text-[10px] text-txtsec uppercase"),
                        html.Th("Mức", className="pb-2 text-left text-[10px] text-txtsec uppercase"),
                        html.Th("Chi tiết", className="pb-2 text-left text-[10px] text-txtsec uppercase"),
                    ])),
                    html.Tbody(table_rows),
                ]),
            ],
        )
    else:
        factor_table = html.Div(
            className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5 text-center",
            children=[
                I("lucide:check-circle", 40, "text-success mx-auto mb-2"),
                html.P("Không phát hiện yếu tố nguy cơ đáng kể.",
                       className="text-sm text-txtsec"),
            ],
        )

    # Advice cards
    advice_items = []
    advice_data = [
        (row["chol"] > THRESHOLDS["chol"],
         "lucide:droplets", "Kiểm Soát Lipid",
         "Cholesterol vượt ngưỡng. Xem xét chế độ ăn ít chất béo bão hòa và tập luyện aerobic."),
        (row["trestbps"] > THRESHOLDS["trestbps"],
         "lucide:gauge", "Kiểm Soát Huyết Áp",
         "Huyết áp cao khi nghỉ. Hạn chế muối, duy trì cân nặng, xem xét thuốc hạ áp."),
        (row["thalach"] < THRESHOLDS["thalach"],
         "lucide:heart-pulse", "Cải Thiện Thể Lực",
         "Nhịp tim tối đa thấp — dấu hiệu giảm khả năng gắng sức. Chương trình phục hồi tim mạch được khuyến nghị."),
        (row["oldpeak"] > THRESHOLDS["oldpeak"],
         "lucide:activity", "Theo Dõi Thiếu Máu Cơ Tim",
         "ST depression đáng kể. Cần đánh giá thêm bằng test gắng sức hoặc chụp mạch vành."),
        (row["fbs"] == 1,
         "lucide:candy", "Quản Lý Đường Huyết",
         "Đường huyết lúc đói > 120 mg/dl. Xét nghiệm HbA1c và tư vấn dinh dưỡng."),
        (row["ca"] > 0,
         "lucide:git-branch", "Đánh Giá Mạch Vành",
         f'{int(row["ca"])} mạch bị fluoroscopy phát hiện. Cần hội chẩn tim mạch can thiệp.'),
        (row["exang"] == 1,
         "lucide:zap", "Quản Lý Đau Ngực Gắng Sức",
         "Xuất hiện đau ngực khi vận động. Tránh gắng sức đột ngột, mang theo nitroglycerin."),
        (row["cp"] == 0,
         "lucide:shield-alert", "Cảnh Giác Thiếu Máu Thầm Lặng",
         "Không có triệu chứng đau ngực điển hình — dễ bỏ sót. Kiểm tra định kỳ là bắt buộc."),
    ]
    for active, icon, title, text in advice_data:
        if active:
            advice_items.append(
                html.Div(
                    className=(
                        "bg-card border border-neonbrd/30 rounded-lg p-4 "
                        "hover:border-neonbrd transition-all"
                    ),
                    children=[
                        html.Div(className="flex items-center gap-2 mb-2", children=[
                            I(icon, 18, "text-warning"),
                            html.H4(title, className="text-sm font-semibold text-txtpri"),
                        ]),
                        html.P(text, className="text-xs text-txtsec leading-relaxed"),
                    ],
                )
            )

    advice_section = html.Div(
        className="mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:clipboard-list", 20, "text-neon"),
                html.H3("Khuyến Nghị Lâm Sàng", className="text-base font-bold text-txtpri"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4",
                     children=advice_items) if advice_items else html.P(
                "Không có khuyến nghị đặc biệt.", className="text-sm text-txtsec"),
        ],
    )

    # Checklist
    check_items = [
        ("Khám tim mạch định kỳ 6 tháng", "lucide:calendar-check"),
        ("Xét nghiệm lipid máu 3 tháng", "lucide:flask-conical"),
        ("Đo huyết áp hàng ngày", "lucide:gauge"),
        ("Tập thể dục 150 phút/tuần", "lucide:dumbbell"),
        ("Chế độ ăn DASH / Mediterranean", "lucide:salad"),
        ("Kiểm soát stress & giấc ngủ", "lucide:moon"),
    ]
    checklist_section = html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:list-todo", 18, "text-neon"),
                html.H3("Core Checklist", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Ul(
                className="space-y-2",
                children=[
                    html.Li(
                        className="flex items-center gap-2 text-sm text-txtsec",
                        children=[I(ic, 15, "text-neon/60"), t],
                    )
                    for t, ic in check_items
                ],
            ),
        ],
    )

    return html.Div([kpi_row, badge, waterfall_card, factor_table, advice_section, checklist_section])
