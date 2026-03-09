"""Page 3 — Phân Tích Lâm Sàng (Clinical Deep-Dive)"""
import dash, numpy as np
from dash import html, dcc, callback, Input, Output
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from components.theme import get_theme

dash.register_page(__name__, path="/clinical-deep-dive", name="Phân Tích Lâm Sàng", order=2)

I = lambda name, sz=20, cls="": DashIconify(icon=name, width=sz, className=cls)


def _chart_card(icon, title, subtitle, graph_id, height=None):
    return html.Div(
        className=(
            "bg-card border border-neonbrd/30 rounded-xl p-5 "
            "hover:border-neonbrd hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all"
        ),
        style={"height": height} if height else {},
        children=[
            html.Div(className="flex items-center gap-2 mb-1", children=[
                I(icon, 18, "text-neon"), html.H3(title, className="text-sm font-semibold text-txtpri"),
            ]),
            html.P(subtitle, className="text-xs text-txtsec mb-4"),
            dcc.Graph(id=graph_id, config={"displayModeBar": False}),
        ],
    )


def _hist_with_threshold(dff, col, threshold, unit, T, col_label=None, flip=False):
    """Histogram chồng lớp cho 2 nhóm bệnh / không bệnh + đường ngưỡng.

    flip=True  → giá trị DƯỚI ngưỡng là xấu  (dùng cho thalach)
    flip=False → giá trị TRÊN ngưỡng là xấu  (dùng cho chol, trestbps)
    """
    fig = go.Figure()
    groups = [
        (0, "Không bệnh tim", T["success"]),
        (1, "Có bệnh tim",   T["danger"]),
    ]
    display_name = col_label or col.upper()

    for val, label, color in groups:
        sub = dff[dff["target"] == val]
        fig.add_trace(go.Histogram(
            x=sub[col], name=label, marker_color=color,
            opacity=0.6, nbinsx=25,
            hovertemplate=f"<b>{label}</b><br>{display_name}: %{{x}} {unit}<br>Số BN: %{{y}}<extra></extra>",
        ))

    # ── Đường ngưỡng ──
    fig.add_vline(
        x=threshold, line_dash="dash", line_color=T["warning"], line_width=2.5,
    )
    # Label ngưỡng phía trên biểu đồ
    fig.add_annotation(
        x=threshold, y=1.06, yref="paper", showarrow=False,
        text=f"<b>⚠ Ngưỡng {threshold} {unit}</b>",
        font=dict(size=12, color=T["warning"]),
        bgcolor=T["paper_bg"], borderpad=3,
    )

    # ── Tính % vượt/dưới ngưỡng → annotation ──
    for val, label, color in groups:
        sub = dff[dff["target"] == val]
        if flip:
            bad_pct = (sub[col] < threshold).mean() * 100
            direction = "dưới"
        else:
            bad_pct = (sub[col] > threshold).mean() * 100
            direction = "trên"
        fig.add_annotation(
            x=0.98 if val == 1 else 0.02,
            y=0.97 - val * 0.09,
            xref="paper", yref="paper",
            xanchor="right" if val == 1 else "left",
            showarrow=False,
            text=(
                f"<b style='color:{color}'>{label}</b>: "
                f"<b>{bad_pct:.0f}%</b> {direction} ngưỡng"
            ),
            font=dict(size=12, color=T["font_color"]),
            bgcolor=T["paper_bg"], borderpad=4,
            opacity=0.9,
        )

    # ── Vùng tô nhạt bên nguy cơ ──
    y_max_approx = len(dff) * 0.15  # ước lượng đỉnh histogram
    if flip:
        fig.add_vrect(
            x0=dff[col].min() * 0.95, x1=threshold,
            fillcolor=T["danger"], opacity=0.06, line_width=0,
            annotation_text="Vùng nguy cơ", annotation_position="top left",
            annotation_font=dict(size=10, color=T["danger"]),
        )
    else:
        fig.add_vrect(
            x0=threshold, x1=dff[col].max() * 1.05,
            fillcolor=T["danger"], opacity=0.06, line_width=0,
            annotation_text="Vùng nguy cơ", annotation_position="top right",
            annotation_font=dict(size=10, color=T["danger"]),
        )

    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        barmode="overlay",
        xaxis_title=f"{display_name} ({unit})",
        yaxis_title="Số bệnh nhân",
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
        margin=dict(t=40, b=40, l=55, r=20), height=420,
        legend=dict(
            orientation="h", y=-0.15, x=0.5, xanchor="center",
            font=dict(size=12),
        ),
    )
    return fig


layout = html.Div([
    html.Div(className="mb-7", children=[
        html.Div(className="flex items-center gap-3 mb-1", children=[
            I("lucide:microscope", 28, "text-neon"),
            html.H1("Phân Tích Lâm Sàng", className="text-2xl font-extrabold text-txtpri tracking-tight"),
        ]),
        html.P("Clinical Deep-Dive — So sánh chỉ số lâm sàng giữa nhóm bệnh và không bệnh",
               className="text-sm text-txtsec"),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        _chart_card("lucide:test-tubes", "Cholesterol (chol)",
                     "Phân phối chol — ngưỡng 200 mg/dl", "violin-chol"),
        _chart_card("lucide:gauge", "Huyết Áp Nghỉ (trestbps)",
                     "Phân phối trestbps — ngưỡng 130 mmHg", "violin-bp"),
        _chart_card("lucide:heart-pulse", "Nhịp Tim Tối Đa (thalach)",
                     "Phân phối thalach — ngưỡng 140 bpm", "violin-thalach"),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        _chart_card("lucide:bar-chart-horizontal", "Nghịch Lý Đau Ngực",
                     "Stacked 100% — phân bố target theo loại đau ngực (cp)", "stacked-cp"),
        _chart_card("lucide:candy", "Đường Huyết Lúc Đói (fbs)",
                     "Tỷ lệ fbs > 120 mg/dl chia theo bệnh", "bar-fbs"),
        _chart_card("lucide:activity", "Điện Tâm Đồ (restecg)",
                     "Phân bố loại ECG chia theo bệnh", "bar-restecg"),
    ]),
    # ── Insight Panel ──
    html.Div(
        className="bg-neonsoft/20 border border-neon/30 rounded-xl p-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:lightbulb", 18, "text-warning"),
                html.H3("Nhận Xét & Insight — Lâm Sàng", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Ul(id="clinical-insights", className="space-y-2 text-sm text-txtsec list-disc list-inside leading-relaxed"),
        ],
    ),
])


@callback(Output("violin-chol", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_violin_chol(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    return _hist_with_threshold(dff, "chol", 200, "mg/dl", T, "Cholesterol")


@callback(Output("violin-bp", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_violin_bp(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    return _hist_with_threshold(dff, "trestbps", 130, "mmHg", T, "Huyết áp nghỉ")


@callback(Output("violin-thalach", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_violin_thalach(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    return _hist_with_threshold(dff, "thalach", 140, "bpm", T, "Nhịp tim tối đa", flip=True)


@callback(Output("stacked-cp", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_stacked_cp(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
              2: "Đau không điển hình", 3: "Không do mạch vành"}
    dff["cp_label"] = dff["cp"].map(cp_map)
    ct = pd.crosstab(dff["cp_label"], dff["target"], normalize="index") * 100
    fig = go.Figure()
    for col_val, label, color in [(0, "Không bệnh", T["success"]),
                                   (1, "Có bệnh", T["danger"])]:
        if col_val in ct.columns:
            fig.add_trace(go.Bar(
                y=ct.index, x=ct[col_val], name=label, orientation="h",
                marker_color=color, text=ct[col_val].round(1).astype(str) + "%",
                textposition="inside",
                hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
            ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        barmode="stack", xaxis_title="Tỷ lệ %",
        margin=dict(t=10, b=40, l=140, r=10), height=420,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor=T["grid_color"], range=[0, 100]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )
    return fig


@callback(Output("bar-fbs", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_bar_fbs(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    ct = pd.crosstab(dff["fbs"], dff["target"])
    fbs_labels = {0: "FBS ≤ 120", 1: "FBS > 120"}
    fig = go.Figure()
    for col_val, label, color in [(0, "Không bệnh", T["success"]),
                                   (1, "Có bệnh", T["danger"])]:
        if col_val in ct.columns:
            fig.add_trace(go.Bar(
                x=[fbs_labels.get(i, str(i)) for i in ct.index],
                y=ct[col_val], name=label, marker_color=color,
                text=ct[col_val], textposition="auto",
                hovertemplate="%{x}: %{y} BN<extra></extra>",
            ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        barmode="group", yaxis_title="Số bệnh nhân",
        margin=dict(t=10, b=40, l=50, r=10), height=420,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )
    return fig


@callback(Output("bar-restecg", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_bar_restecg(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    ecg_map = {0: "Bình thường", 1: "Bất thường ST-T", 2: "Dày thất trái"}
    ct = pd.crosstab(dff["restecg"], dff["target"])
    fig = go.Figure()
    for col_val, label, color in [(0, "Không bệnh", T["success"]),
                                   (1, "Có bệnh", T["danger"])]:
        if col_val in ct.columns:
            fig.add_trace(go.Bar(
                x=[ecg_map.get(i, str(i)) for i in ct.index],
                y=ct[col_val], name=label, marker_color=color,
                text=ct[col_val], textposition="auto",
                hovertemplate="%{x}: %{y} BN<extra></extra>",
            ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        barmode="group", yaxis_title="Số bệnh nhân",
        margin=dict(t=10, b=40, l=50, r=10), height=420,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )
    return fig


@callback(Output("clinical-insights", "children"), Input("filtered-data-store", "data"))
def update_clinical_insights(json_data):
    if json_data is None:
        return []
    dff = pd.read_json(StringIO(json_data), orient="split")
    if len(dff) == 0:
        return [html.Li("Không có dữ liệu phù hợp bộ lọc.")]

    insights = []
    sick = dff[dff["target"] == 1]
    healthy = dff[dff["target"] == 0]

    # Cholesterol
    if len(sick) > 0 and len(healthy) > 0:
        sick_high_chol = (sick["chol"] > 200).mean() * 100
        healthy_high_chol = (healthy["chol"] > 200).mean() * 100
        insights.append(html.Li([
            html.Strong("Cholesterol: "),
            f"Nhóm bệnh: {sick_high_chol:.0f}% vượt 200 mg/dl vs Không bệnh: {healthy_high_chol:.0f}%. ",
            "Sự khác biệt không quá lớn — cholesterol đơn lẻ không phải yếu tố quyết định."
            if abs(sick_high_chol - healthy_high_chol) < 10
            else "Nhóm bệnh có tỷ lệ cholesterol cao rõ rệt hơn."
        ]))

    # Blood pressure
    if len(sick) > 0 and len(healthy) > 0:
        sick_bp = sick["trestbps"].mean()
        healthy_bp = healthy["trestbps"].mean()
        insights.append(html.Li([
            html.Strong("Huyết áp nghỉ: "),
            f"TB nhóm bệnh: {sick_bp:.0f} mmHg, không bệnh: {healthy_bp:.0f} mmHg. ",
            "Huyết áp cao liên quan đến tăng nguy cơ bệnh tim."
            if sick_bp > healthy_bp else
            "Huyết áp trung bình khá tương đồng giữa 2 nhóm."
        ]))

    # Thalach
    if len(sick) > 0 and len(healthy) > 0:
        sick_thalach = sick["thalach"].mean()
        healthy_thalach = healthy["thalach"].mean()
        insights.append(html.Li([
            html.Strong("Nhịp tim tối đa: "),
            f"Nhóm bệnh: {sick_thalach:.0f} bpm, không bệnh: {healthy_thalach:.0f} bpm. ",
            "Nhóm bệnh có nhịp tim max thấp hơn đáng kể — dấu hiệu giảm khả năng gắng sức tim mạch."
            if sick_thalach < healthy_thalach else
            "Nhịp tim tối đa tương đương giữa 2 nhóm."
        ]))

    # Chest pain paradox
    cp0_sick_rate = (dff[dff["cp"] == 0]["target"].mean() * 100) if (dff["cp"] == 0).any() else 0
    insights.append(html.Li([
        html.Strong("Nghịch lý đau ngực: "),
        f"{cp0_sick_rate:.0f}% bệnh nhân 'không triệu chứng' (cp=0) thực tế có bệnh tim. ",
        "Đây là phát hiện quan trọng: không có đau ngực ≠ không có bệnh tim. Sàng lọc chủ động rất cần thiết."
    ]))

    # FBS
    fbs_sick = (sick["fbs"] == 1).mean() * 100 if len(sick) > 0 else 0
    fbs_healthy = (healthy["fbs"] == 1).mean() * 100 if len(healthy) > 0 else 0
    insights.append(html.Li([
        html.Strong("Đường huyết: "),
        f"FBS > 120: Nhóm bệnh {fbs_sick:.0f}%, Không bệnh {fbs_healthy:.0f}%. ",
        "Đường huyết cao không nhất thiết phân biệt 2 nhóm — yếu tố này cần kết hợp với các chỉ số khác."
    ]))

    return insights
