"""Page 0 — Khám Phá Dữ Liệu & EDA (Data Description & Exploratory Analysis)"""
import dash
from dash import html, dcc, callback, Input, Output, dash_table
from dash_iconify import DashIconify
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from io import StringIO
from components.theme import get_theme

dash.register_page(
    __name__,
    path="/eda",
    name="Khám Phá Dữ Liệu",
    order=-1,  # appear before overview
)

I = lambda name, sz=20, cls="": DashIconify(icon=name, width=sz, className=cls)

# ── Static dataset info (loaded once) ──
_DF = pd.read_csv("heart.csv")
_DF.columns = _DF.columns.str.strip()

VARIABLE_INFO = [
    ("age",      "Tuổi",                "int64",    "Tuổi bệnh nhân (năm)"),
    ("sex",      "Giới tính",           "int64",    "0 = Nữ, 1 = Nam"),
    ("cp",       "Loại đau ngực",       "int64",    "0 = Không triệu chứng, 1 = Đau điển hình, 2 = Đau không điển hình, 3 = Không do mạch vành"),
    ("trestbps", "Huyết áp nghỉ",      "int64",    "Huyết áp lúc nghỉ (mmHg)"),
    ("chol",     "Cholesterol",         "int64",    "Cholesterol huyết thanh (mg/dl)"),
    ("fbs",      "Đường huyết đói",     "int64",    "1 nếu fbs > 120 mg/dl, 0 ngược lại"),
    ("restecg",  "Điện tâm đồ nghỉ",   "int64",    "0 = Bình thường, 1 = Bất thường ST-T, 2 = Dày thất trái"),
    ("thalach",  "Nhịp tim tối đa",     "int64",    "Nhịp tim tối đa đạt được (bpm)"),
    ("exang",    "Đau khi vận động",    "int64",    "1 = Có, 0 = Không"),
    ("oldpeak",  "ST depression",       "float64",  "Chênh lệch ST do vận động so với nghỉ"),
    ("slope",    "Slope ST",            "int64",    "0 = Dốc xuống, 1 = Phẳng, 2 = Dốc lên"),
    ("ca",       "Số mạch tắc",        "int64",    "Số mạch máu lớn (0–3) phát hiện qua fluoroscopy"),
    ("thal",     "Thalassemia",         "int64",    "1 = Bình thường, 2 = Khuyết cố định, 3 = Khuyết hồi phục"),
    ("target",   "Chẩn đoán",          "int64",    "1 = Có bệnh tim, 0 = Không bệnh tim"),
]


def _info_card(icon, color, label, value, sub=""):
    return html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-4 text-center",
        children=[
            I(icon, 28, f"text-{color} mx-auto mb-2"),
            html.P(label, className="text-[10px] text-txtsec uppercase tracking-wide mb-1"),
            html.P(value, className="text-2xl font-bold text-txtpri"),
            html.P(sub, className="text-xs text-txtsec mt-1") if sub else None,
        ],
    )


# ── Layout ──
layout = html.Div([
    # ── Header ──
    html.Div(className="mb-7", children=[
        html.Div(className="flex items-center gap-3 mb-1", children=[
            I("lucide:database", 28, "text-neon"),
            html.H1("Khám Phá Dữ Liệu & EDA",
                     className="text-2xl font-extrabold text-txtpri tracking-tight"),
        ]),
        html.P("Data Description & Exploratory Data Analysis — Tìm hiểu bộ dữ liệu Heart Disease Cleveland UCI",
               className="text-sm text-txtsec"),
    ]),

    # ── Section 1: Nguồn dữ liệu ──
    html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:info", 18, "text-neon"),
                html.H3("Nguồn Dữ Liệu", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Div(className="text-sm text-txtsec leading-relaxed space-y-2", children=[
                html.P([
                    html.Strong("Dataset: ", className="text-txtpri"),
                    "Heart Disease Dataset — Cleveland Clinic Foundation (UCI Machine Learning Repository)"
                ]),
                html.P([
                    html.Strong("Lĩnh vực: ", className="text-txtpri"),
                    "Y tế — Chẩn đoán bệnh tim mạch (Cardiovascular Disease Diagnosis)"
                ]),
                html.P([
                    html.Strong("Mục tiêu: ", className="text-txtpri"),
                    "Dự đoán bệnh nhân có mắc bệnh tim hay không (biến target: 0/1) dựa trên 13 đặc trưng lâm sàng."
                ]),
                html.P([
                    html.Strong("Nguồn: ", className="text-txtpri"),
                    html.A("https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset",
                           href="https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset",
                           className="text-neon underline", target="_blank"),
                ]),
            ]),
        ],
    ),

    # ── Section 2: Dataset KPIs ──
    html.Div(id="eda-kpi-row",
             className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4 mb-5"),

    # ── Section 3: Bảng mô tả biến ──
    html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:table-2", 18, "text-neon"),
                html.H3("Mô Tả Biến (Data Dictionary)", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Div(className="overflow-x-auto", children=[
                html.Table(className="w-full text-sm", children=[
                    html.Thead(html.Tr([
                        html.Th("Tên biến", className="pb-2 text-left text-[10px] text-txtsec uppercase px-3"),
                        html.Th("Tên tiếng Việt", className="pb-2 text-left text-[10px] text-txtsec uppercase px-3"),
                        html.Th("Kiểu dữ liệu", className="pb-2 text-left text-[10px] text-txtsec uppercase px-3"),
                        html.Th("Mô tả", className="pb-2 text-left text-[10px] text-txtsec uppercase px-3"),
                    ])),
                    html.Tbody([
                        html.Tr(
                            className="border-b border-neonbrd/20 hover:bg-neonsoft/30",
                            children=[
                                html.Td(html.Code(col, className="text-neon text-xs bg-neonsoft/20 px-1.5 py-0.5 rounded"),
                                        className="py-2.5 px-3"),
                                html.Td(vi_name, className="py-2.5 px-3 text-txtpri font-medium"),
                                html.Td(html.Code(dtype, className="text-warning text-xs"), className="py-2.5 px-3"),
                                html.Td(desc, className="py-2.5 px-3 text-txtsec"),
                            ],
                        )
                        for col, vi_name, dtype, desc in VARIABLE_INFO
                    ]),
                ]),
            ]),
        ],
    ),

    # ── Section 4: Thống kê mô tả ──
    html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:bar-chart-4", 18, "text-neon"),
                html.H3("Thống Kê Mô Tả (Descriptive Statistics)", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Bảng describe() hiển thị count, mean, std, min, Q1, median, Q3, max cho mỗi biến số.",
                   className="text-xs text-txtsec mb-4"),
            html.Div(id="eda-describe-table", className="overflow-x-auto"),
        ],
    ),

    # ── Section 5: Missing Values ──
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        html.Div(
            className="bg-card border border-neonbrd/30 rounded-xl p-5",
            children=[
                html.Div(className="flex items-center gap-2 mb-3", children=[
                    I("lucide:alert-circle", 18, "text-neon"),
                    html.H3("Phân Tích Giá Trị Thiếu (Missing Values)", className="text-sm font-semibold text-txtpri"),
                ]),
                dcc.Graph(id="eda-missing-chart", config={"displayModeBar": False}),
            ],
        ),
    ]),

    # ── Section 6: Outlier Detection ──
    html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:scan-search", 18, "text-neon"),
                html.H3("Phát Hiện Outlier (IQR Method)", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Biểu đồ tổng hợp số lượng outlier theo phương pháp IQR (1.5×IQR) cho mỗi biến liên tục.",
                   className="text-xs text-txtsec mb-4"),
            dcc.Graph(id="eda-outlier-bar", config={"displayModeBar": False}),
            html.Div(id="eda-outlier-summary", className="mt-3"),
            html.Div(className="mt-5", children=[
                html.Div(className="flex items-center gap-2 mb-3", children=[
                    I("lucide:box-select", 18, "text-neon"),
                    html.H3("Boxplot Chi Tiết Từng Biến", className="text-sm font-semibold text-txtpri"),
                ]),
                html.P("Mỗi biến hiển thị riêng với thang đo phù hợp — dễ nhận diện outlier hơn.",
                       className="text-xs text-txtsec mb-4"),
                dcc.Graph(id="eda-outlier-box", config={"displayModeBar": False}),
            ]),
        ],
    ),

    # ── Section 7: Pivot Table ──
    html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:table", 18, "text-neon"),
                html.H3("Pivot Table — Thống Kê Nhóm", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Giá trị trung bình các chỉ số lâm sàng theo Giới tính × Chẩn đoán (GroupBy + Pivot).",
                   className="text-xs text-txtsec mb-4"),
            html.Div(id="eda-pivot-table", className="overflow-x-auto"),
        ],
    ),

    # ── Section 8: Biểu đồ phân phối biến target ──
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        html.Div(
            className="bg-card border border-neonbrd/30 rounded-xl p-5",
            children=[
                html.Div(className="flex items-center gap-2 mb-3", children=[
                    I("lucide:pie-chart", 18, "text-neon"),
                    html.H3("Phân Phối Biến Mục Tiêu (Target Distribution)", className="text-sm font-semibold text-txtpri"),
                ]),
                dcc.Graph(id="eda-target-dist", config={"displayModeBar": False}),
            ],
        ),
    ]),

    # ── Section 9: Raw Data Table ──
    html.Div(
        className="bg-card border border-neonbrd/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:sheet", 18, "text-neon"),
                html.H3("Bảng Dữ Liệu Gốc (Data Table)", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Bảng hiển thị 20 dòng đầu tiên (có thể sắp xếp, lọc). Dữ liệu phản ứng theo bộ lọc Sidebar.",
                   className="text-xs text-txtsec mb-4"),
            html.Div(id="eda-datatable-wrapper"),
        ],
    ),

    # ── Insight Panel ──
    html.Div(
        className="bg-neonsoft/20 border border-neon/30 rounded-xl p-5 mb-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:lightbulb", 18, "text-warning"),
                html.H3("Nhận Xét & Insight — Phần EDA", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Ul(id="eda-insights", className="space-y-2 text-sm text-txtsec list-disc list-inside leading-relaxed"),
        ],
    ),
])


# ════════════════════════════════════════════════════
# Callbacks
# ════════════════════════════════════════════════════

@callback(
    [Output("eda-kpi-row", "children"),
     Output("eda-describe-table", "children"),
     Output("eda-missing-chart", "figure"),
     Output("eda-outlier-bar", "figure"),
     Output("eda-outlier-box", "figure"),
     Output("eda-outlier-summary", "children"),
     Output("eda-pivot-table", "children"),
     Output("eda-target-dist", "figure"),
     Output("eda-datatable-wrapper", "children"),
     Output("eda-insights", "children")],
    [Input("filtered-data-store", "data"),
     Input("theme-store", "data")],
)
def update_eda(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        empty = go.Figure()
        return [], "", empty, empty, empty, "", "", empty, "", []

    dff = pd.read_json(StringIO(json_data), orient="split")

    # ─────────────────────────────────
    # 1. KPI cards
    # ─────────────────────────────────
    n_rows, n_cols = dff.shape
    n_missing = int(dff.isnull().sum().sum())
    n_duplicates = int(dff.duplicated().sum())
    n_numeric = len(dff.select_dtypes(include="number").columns)
    target_rate = dff["target"].mean() * 100 if "target" in dff else 0

    kpis = [
        _info_card("lucide:rows-3", "neon", "Số dòng", f"{n_rows:,}"),
        _info_card("lucide:columns-3", "neon", "Số cột", f"{n_cols}"),
        _info_card("lucide:alert-circle", "danger", "Giá trị thiếu", f"{n_missing}",
                   "0 missing ✓" if n_missing == 0 else f"{n_missing} cells"),
        _info_card("lucide:copy", "warning", "Dòng trùng lặp", f"{n_duplicates}",
                   f"{n_duplicates/n_rows*100:.1f}%" if n_rows else ""),
        _info_card("lucide:hash", "success", "Biến số", f"{n_numeric}"),
        _info_card("lucide:heart-pulse", "danger", "Tỷ lệ bệnh", f"{target_rate:.1f}%"),
    ]

    # ─────────────────────────────────
    # 2. Descriptive statistics table
    # ─────────────────────────────────
    desc = dff.describe().T.round(2)
    desc.insert(0, "Biến", desc.index)
    desc_table = html.Table(
        className="w-full text-sm",
        children=[
            html.Thead(html.Tr([
                html.Th(col, className="pb-2 text-left text-[10px] text-txtsec uppercase px-2 whitespace-nowrap")
                for col in desc.columns
            ])),
            html.Tbody([
                html.Tr(
                    className="border-b border-neonbrd/20",
                    children=[
                        html.Td(
                            html.Code(str(val), className="text-neon text-xs") if i == 0
                            else str(val),
                            className="py-2 px-2 text-txtpri whitespace-nowrap"
                        )
                        for i, val in enumerate(row)
                    ],
                )
                for _, row in desc.iterrows()
            ]),
        ],
    )

    # ─────────────────────────────────
    # 3. Missing values chart
    # ─────────────────────────────────
    missing_counts = dff.isnull().sum()
    missing_pct = (dff.isnull().mean() * 100).round(2)
    has_missing = missing_counts.sum() > 0

    fig_missing = go.Figure()
    colors = [T["danger"] if v > 0 else T["success"] for v in missing_counts.values]
    fig_missing.add_trace(go.Bar(
        x=missing_counts.index, y=missing_counts.values,
        marker_color=colors,
        text=[f"{v} ({p:.1f}%)" for v, p in zip(missing_counts.values, missing_pct.values)],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Missing: %{y} (%{text})<extra></extra>",
    ))
    if not has_missing:
        fig_missing.add_annotation(
            x=0.5, y=0.5, xref="paper", yref="paper",
            text="✅ Không có giá trị thiếu (Missing = 0 cho tất cả biến)",
            showarrow=False, font=dict(size=16, color=T["success"]),
        )
    fig_missing.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        xaxis_title="Biến", yaxis_title="Số lượng Missing",
        margin=dict(t=20, b=40, l=50, r=10), height=350,
        xaxis=dict(gridcolor=T["grid_color"], tickangle=-45),
        yaxis=dict(gridcolor=T["grid_color"]),
    )

    # ─────────────────────────────────
    # 4. Outlier detection
    # ─────────────────────────────────
    numeric_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    col_labels = {"age": "Tuổi", "trestbps": "Huyết áp nghỉ",
                  "chol": "Cholesterol", "thalach": "Nhịp tim max",
                  "oldpeak": "ST chênh"}
    col_units = {"age": "tuổi", "trestbps": "mmHg",
                 "chol": "mg/dl", "thalach": "bpm", "oldpeak": "mm"}
    available_cols = [c for c in numeric_cols if c in dff.columns]

    outlier_data = {}  # col -> {n, lower, upper, pct}
    outlier_summary_items = []
    for col in available_cols:
        q1 = dff[col].quantile(0.25)
        q3 = dff[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        n_out = int(((dff[col] < lower) | (dff[col] > upper)).sum())
        pct = n_out / len(dff) * 100 if len(dff) > 0 else 0
        outlier_data[col] = {"n": n_out, "lower": lower, "upper": upper, "pct": pct}
        if n_out > 0:
            outlier_summary_items.append(
                html.Li([
                    html.Code(col, className="text-neon text-xs mr-1"),
                    f": {n_out} outlier ({pct:.1f}%) — Biên IQR: [{lower:.1f}, {upper:.1f}] {col_units.get(col, '')}"
                ], className="text-sm text-txtsec")
            )

    # 4a. Bar chart — số lượng outlier per biến
    fig_outlier_bar = go.Figure()
    bar_names = [col_labels.get(c, c) for c in available_cols]
    bar_counts = [outlier_data[c]["n"] for c in available_cols]
    bar_pcts = [outlier_data[c]["pct"] for c in available_cols]
    bar_colors = [T["danger"] if n > 0 else T["success"] for n in bar_counts]

    fig_outlier_bar.add_trace(go.Bar(
        x=bar_names, y=bar_counts,
        marker_color=bar_colors,
        text=[f"<b>{n}</b> ({p:.1f}%)" for n, p in zip(bar_counts, bar_pcts)],
        textposition="auto",
        textfont=dict(size=13),
        hovertemplate="<b>%{x}</b><br>Outlier: %{y} (%{text})<extra></extra>",
    ))
    total_outliers = sum(bar_counts)
    fig_outlier_bar.add_annotation(
        x=0.5, y=1.08, xref="paper", yref="paper",
        text=f"Tổng: <b>{total_outliers}</b> outlier trên {len(dff)} dòng ({total_outliers/len(dff)*100:.1f}%)" if len(dff) > 0 else "",
        showarrow=False, font=dict(size=13, color=T["font_color"]),
    )
    fig_outlier_bar.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        xaxis_title="Biến", yaxis_title="Số lượng Outlier",
        margin=dict(t=40, b=40, l=50, r=10), height=350,
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )

    # 4b. Subplots — boxplot riêng từng biến (mỗi biến có scale riêng)
    n_vars = len(available_cols)
    fig_outlier_sub = make_subplots(
        rows=1, cols=n_vars,
        subplot_titles=[f"{col_labels.get(c, c)} ({col_units.get(c, '')})" for c in available_cols],
        horizontal_spacing=0.06,
    )
    for i, col in enumerate(available_cols):
        color = T["bar_colors"][i % len(T["bar_colors"])]
        info = outlier_data[col]
        fig_outlier_sub.add_trace(
            go.Box(
                y=dff[col], name=col_labels.get(col, col),
                marker_color=color, boxpoints="outliers",
                boxmean="sd",
                hovertemplate=f"<b>{col_labels.get(col, col)}</b><br>%{{y}} {col_units.get(col, '')}<extra></extra>",
            ),
            row=1, col=i + 1,
        )
        # Vẽ đường giới hạn IQR
        for bound, lbl in [(info["lower"], "Lower"), (info["upper"], "Upper")]:
            fig_outlier_sub.add_hline(
                y=bound, line_dash="dot", line_color=T["warning"], line_width=1.5,
                annotation_text=f"{lbl}: {bound:.1f}",
                annotation_font=dict(size=9, color=T["warning"]),
                annotation_position="top right" if lbl == "Upper" else "bottom right",
                row=1, col=i + 1,
            )

    fig_outlier_sub.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        showlegend=False, margin=dict(t=40, b=20, l=40, r=10), height=420,
    )
    # Áp dụng grid color cho từng subplot
    for i in range(n_vars):
        axis_suffix = "" if i == 0 else str(i + 1)
        fig_outlier_sub.update_yaxes(gridcolor=T["grid_color"], row=1, col=i + 1)
        fig_outlier_sub.update_xaxes(gridcolor=T["grid_color"], row=1, col=i + 1)

    outlier_summary = html.Div(children=[
        html.P([I("lucide:alert-triangle", 14, "text-warning mr-1 inline-block"),
                html.Strong(f"Tổng cộng phát hiện outlier ở {len(outlier_summary_items)} biến:")],
               className="text-sm text-txtpri mb-1") if outlier_summary_items else None,
        html.Ul(outlier_summary_items, className="list-disc list-inside") if outlier_summary_items
        else html.P("✅ Không phát hiện outlier rõ rệt.", className="text-sm text-success"),
    ])

    # ─────────────────────────────────
    # 5. Pivot table (sex × target → mean of clinical vars)
    # ─────────────────────────────────
    sex_map = {0: "Nữ", 1: "Nam"}
    target_map = {0: "Không bệnh", 1: "Có bệnh"}
    pivot_df = dff.copy()
    pivot_df["Giới tính"] = pivot_df["sex"].map(sex_map)
    pivot_df["Chẩn đoán"] = pivot_df["target"].map(target_map)
    pivot_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    pivot_available = [c for c in pivot_cols if c in pivot_df.columns]

    pivot = pivot_df.groupby(["Giới tính", "Chẩn đoán"])[pivot_available].mean().round(1)
    pivot = pivot.reset_index()

    pivot_table = html.Table(
        className="w-full text-sm",
        children=[
            html.Thead(html.Tr([
                html.Th(col, className="pb-2 text-left text-[10px] text-txtsec uppercase px-3 whitespace-nowrap")
                for col in pivot.columns
            ])),
            html.Tbody([
                html.Tr(
                    className="border-b border-neonbrd/20",
                    children=[
                        html.Td(str(val), className="py-2 px-3 text-txtpri whitespace-nowrap font-medium"
                                if i < 2 else "py-2 px-3 text-txtpri whitespace-nowrap")
                        for i, val in enumerate(row)
                    ],
                )
                for _, row in pivot.iterrows()
            ]),
        ],
    )

    # ─────────────────────────────────
    # 6. Target distribution bar
    # ─────────────────────────────────
    fig_target = go.Figure()
    target_counts = dff["target"].value_counts().sort_index()
    fig_target.add_trace(go.Bar(
        x=["Không bệnh tim (0)", "Có bệnh tim (1)"],
        y=[target_counts.get(0, 0), target_counts.get(1, 0)],
        marker_color=[T["success"], T["danger"]],
        text=[target_counts.get(0, 0), target_counts.get(1, 0)],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Số BN: %{y}<extra></extra>",
    ))
    fig_target.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        yaxis_title="Số bệnh nhân", margin=dict(t=10, b=40, l=50, r=10), height=350,
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )

    # ─────────────────────────────────
    # 7. Data table (first 20 rows)
    # ─────────────────────────────────
    display_df = dff.head(20).round(2)
    datatable = dash_table.DataTable(
        data=display_df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in display_df.columns],
        sort_action="native",
        filter_action="native",
        page_size=10,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": T["paper_bg"],
            "color": T["font_color"],
            "fontWeight": "600",
            "fontSize": "11px",
            "textTransform": "uppercase",
            "borderBottom": f"2px solid {T['neon']}",
        },
        style_cell={
            "backgroundColor": T["paper_bg"],
            "color": T["font_color"],
            "fontSize": "12px",
            "padding": "6px 10px",
            "border": f"1px solid {T['grid_color']}",
            "whiteSpace": "nowrap",
        },
        style_filter={
            "backgroundColor": T["paper_bg"],
            "color": T["font_color"],
        },
    )

    # ─────────────────────────────────
    # 8. Insights
    # ─────────────────────────────────
    insights = []
    insights.append(html.Li([
        html.Strong("Kích thước dataset: "),
        f"{n_rows} dòng × {n_cols} cột. {'Không có giá trị thiếu.' if n_missing == 0 else f'Có {n_missing} giá trị thiếu cần xử lý.'}"
    ]))
    if n_duplicates > 0:
        insights.append(html.Li([
            html.Strong("Dữ liệu trùng lặp: "),
            f"Phát hiện {n_duplicates} dòng trùng ({n_duplicates/n_rows*100:.1f}%). "
            "Có thể do dataset ghép từ nhiều nguồn — cần cân nhắc loại bỏ."
        ]))
    else:
        insights.append(html.Li([
            html.Strong("Dữ liệu trùng lặp: "),
            "Không có dòng trùng lặp."
        ]))

    # Class balance
    if "target" in dff:
        n0 = int((dff["target"] == 0).sum())
        n1 = int((dff["target"] == 1).sum())
        ratio = n1 / n0 if n0 > 0 else 0
        if 0.8 <= ratio <= 1.2:
            insights.append(html.Li([
                html.Strong("Cân bằng lớp: "),
                f"Tương đối cân bằng — Không bệnh: {n0}, Có bệnh: {n1} (tỷ lệ 1:{ratio:.2f})."
            ]))
        else:
            insights.append(html.Li([
                html.Strong("Mất cân bằng lớp: "),
                f"Không bệnh: {n0}, Có bệnh: {n1} (tỷ lệ 1:{ratio:.2f}). Cần chú ý khi huấn luyện mô hình."
            ]))

    # Age range
    if "age" in dff:
        insights.append(html.Li([
            html.Strong("Phân bố tuổi: "),
            f"Từ {int(dff['age'].min())} đến {int(dff['age'].max())} tuổi, trung bình {dff['age'].mean():.1f} ± {dff['age'].std():.1f}."
        ]))

    # Cholesterol insight
    if "chol" in dff:
        high_chol = (dff["chol"] > 200).mean() * 100
        insights.append(html.Li([
            html.Strong("Cholesterol: "),
            f"{high_chol:.1f}% bệnh nhân có cholesterol > 200 mg/dl (mức khuyến cáo)."
        ]))

    # Outlier insight
    if outlier_summary_items:
        insights.append(html.Li([
            html.Strong("Outlier: "),
            f"Phát hiện outlier ở {len(outlier_summary_items)} biến (chol, trestbps, oldpeak…). "
            "Nên kiểm tra và xử lý trước khi phân tích sâu."
        ]))

    return kpis, desc_table, fig_missing, fig_outlier_bar, fig_outlier_sub, outlier_summary, pivot_table, fig_target, datatable, insights
