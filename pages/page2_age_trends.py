"""Page 2 — Xu Hướng Theo Tuổi (Age Trend Analytics)"""
import dash, numpy as np
from dash import html, dcc, callback, Input, Output
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from components.theme import get_theme

dash.register_page(__name__, path="/age-trends", name="Xu Hướng Theo Tuổi", order=1)

I = lambda name, sz=20, cls="": DashIconify(icon=name, width=sz, className=cls)

def _chart_card(icon, title, subtitle, graph_id):
    return html.Div(
        className=(
            "bg-card border border-neonbrd/30 rounded-xl p-5 "
            "hover:border-neonbrd hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all"
        ),
        children=[
            html.Div(className="flex items-center gap-2 mb-1", children=[
                I(icon, 18, "text-neon"), html.H3(title, className="text-sm font-semibold text-txtpri"),
            ]),
            html.P(subtitle, className="text-xs text-txtsec mb-4"),
            dcc.Graph(id=graph_id, config={"displayModeBar": False}),
        ],
    )

layout = html.Div([
    html.Div(className="mb-7", children=[
        html.Div(className="flex items-center gap-3 mb-1", children=[
            I("lucide:trending-up", 28, "text-neon"),
            html.H1("Xu Hướng Theo Tuổi", className="text-2xl font-extrabold text-txtpri tracking-tight"),
        ]),
        html.P("Age Trend Analytics — Phân tích mối quan hệ giữa độ tuổi và bệnh tim",
               className="text-sm text-txtsec"),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        _chart_card("lucide:line-chart", "Tỷ Lệ Bệnh Tim Theo Nhóm Tuổi",
                     "Tỷ lệ % bệnh nhân mắc bệnh tim trong mỗi nhóm 5 tuổi", "line-age"),
        _chart_card("lucide:box-select", "Box-Plot Tuổi vs Kết Quả Chẩn Đoán",
                     "Phân phối tuổi chia theo nhóm bệnh/không bệnh", "box-age"),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        _chart_card("lucide:bar-chart-3", "Histogram Tuổi Theo Giới Tính",
                     "Phân phối tuổi của Nam và Nữ", "hist-age-sex"),
        _chart_card("lucide:grid-3x3", "Heatmap Nhóm Tuổi × Đau Ngực",
                     "Ma trận số lượng giữa nhóm tuổi và loại đau ngực", "heatmap-age-cp"),
    ]),
    # ── Insight Panel ──
    html.Div(
        className="bg-neonsoft/20 border border-neon/30 rounded-xl p-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:lightbulb", 18, "text-warning"),
                html.H3("Nhận Xét & Insight — Xu Hướng Tuổi", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Ul(id="age-insights", className="space-y-2 text-sm text-txtsec list-disc list-inside leading-relaxed"),
        ],
    ),
])


@callback(Output("line-age", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_line_age(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    bins = list(range(20, 85, 5))
    labels = [f"{b}-{b+4}" for b in bins[:-1]]
    dff["age_group"] = pd.cut(dff["age"], bins=bins, labels=labels, right=False)
    grp = dff.groupby("age_group", observed=False)["target"]
    rate = (grp.mean() * 100).round(1)
    cnt = grp.size()
    sick = grp.sum().astype(int)

    # Ngưỡng mẫu nhỏ — tỷ lệ dưới 20 BN không đáng tin
    MIN_SAMPLE = 20

    fig = go.Figure()

    # ── Cột: Số bệnh nhân (tổng) ──
    bar_colors = [T["bar_colors"][0] if n >= MIN_SAMPLE
                  else "rgba(150,150,150,0.35)" for n in cnt.values]
    fig.add_trace(go.Bar(
        x=rate.index.astype(str), y=cnt.values, name="Tổng BN trong nhóm",
        marker_color=bar_colors, opacity=0.5,
        text=[f"<b>{n}</b>" for n in cnt.values], textposition="auto",
        hovertemplate=(
            "<b>Nhóm %{x}</b><br>"
            "Tổng: %{y} bệnh nhân<extra></extra>"
        ),
    ))

    # ── Cột xếp chồng: Số người bệnh (màu đỏ nhạt) ──
    fig.add_trace(go.Bar(
        x=rate.index.astype(str), y=sick.values, name="Số BN có bệnh tim",
        marker_color=T["danger"], opacity=0.55,
        text=[f"{s}" for s in sick.values], textposition="inside",
        textfont=dict(size=10),
        hovertemplate=(
            "<b>Nhóm %{x}</b><br>"
            "Có bệnh: %{y} người<extra></extra>"
        ),
    ))

    # ── Đường: Tỷ lệ bệnh % (trục phải) ──
    # Marker to lớn hơn nếu mẫu đủ, nhỏ + xám nếu mẫu ít
    marker_sizes = [11 if n >= MIN_SAMPLE else 7 for n in cnt.values]
    marker_colors = [T["danger"] if n >= MIN_SAMPLE
                     else "rgba(150,150,150,0.7)" for n in cnt.values]
    line_dashes = None  # solid

    fig.add_trace(go.Scatter(
        x=rate.index.astype(str), y=rate.values, name="Tỷ lệ bệnh %",
        mode="lines+markers+text",
        line=dict(color=T["danger"], width=3),
        marker=dict(size=marker_sizes, color=marker_colors,
                    line=dict(width=2, color=T["font_color"])),
        text=[f"<b>{r:.0f}%</b>" if n >= MIN_SAMPLE
              else f"<i>{r:.0f}%</i><br><sub>n={n}</sub>"
              for r, n in zip(rate.values, cnt.values)],
        textposition="top center",
        textfont=dict(size=11),
        yaxis="y2",
        hovertemplate=(
            "<b>Nhóm %{x}</b><br>"
            "Tỷ lệ bệnh: %{y:.1f}%<extra></extra>"
        ),
    ))

    # ── Annotations cảnh báo mẫu nhỏ ──
    for i, (lbl, n) in enumerate(zip(rate.index.astype(str), cnt.values)):
        if 0 < n < MIN_SAMPLE:
            fig.add_annotation(
                x=lbl, y=rate.values[i], yref="y2",
                text=f"⚠ n={n}", showarrow=True,
                arrowhead=0, arrowcolor=T["warning"],
                ax=0, ay=-30,
                font=dict(size=10, color=T["warning"]),
                bgcolor=T["paper_bg"], borderpad=2,
            )

    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        margin=dict(t=40, b=50, l=55, r=55), height=460, barmode="overlay",
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    font=dict(size=11)),
        xaxis=dict(title="Nhóm tuổi", gridcolor=T["grid_color"]),
        yaxis=dict(title="Số bệnh nhân", gridcolor=T["grid_color"]),
        yaxis2=dict(title="Tỷ lệ bệnh (%)", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)", range=[0, 115]),
    )

    # ── Chú thích giải thích ──
    fig.add_annotation(
        x=0.5, y=-0.28, xref="paper", yref="paper",
        text="<i>Cột xanh = tổng BN · Cột đỏ = số BN có bệnh · Đường = tỷ lệ % bệnh · ⚠ = mẫu nhỏ (< 20), tỷ lệ không đáng tin</i>",
        showarrow=False, font=dict(size=10, color=T["font_color"]),
        opacity=0.6,
    )
    return fig


@callback(Output("box-age", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_box_age(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    fig = go.Figure()
    for val, label, color in [(0, "Không bệnh tim", T["success"]),
                               (1, "Có bệnh tim", T["danger"])]:
        sub = dff[dff["target"] == val]
        fig.add_trace(go.Box(y=sub["age"], name=label, marker_color=color,
                             boxmean="sd",
                             hovertemplate="<b>%{y}</b> tuổi<extra></extra>"))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"],
                      yaxis_title="Tuổi", margin=dict(t=10, b=40, l=50, r=10), height=420,
                      xaxis=dict(gridcolor=T["grid_color"]),
                      yaxis=dict(gridcolor=T["grid_color"]))
    return fig


@callback(Output("hist-age-sex", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_hist_age_sex(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    fig = go.Figure()
    for val, label, color in [(0, "Nữ giới", T["primary"]),
                               (1, "Nam giới", T["danger"])]:
        sub = dff[dff["sex"] == val]
        fig.add_trace(go.Histogram(x=sub["age"], name=label, marker_color=color,
                                   opacity=0.7, nbinsx=15,
                                   hovertemplate="%{x} tuổi: %{y} bệnh nhân<extra></extra>"))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"], barmode="overlay",
                      xaxis_title="Tuổi", yaxis_title="Số bệnh nhân",
                      margin=dict(t=10, b=40, l=50, r=10), height=420,
                      legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                      xaxis=dict(gridcolor=T["grid_color"]),
                      yaxis=dict(gridcolor=T["grid_color"]))
    return fig


@callback(Output("heatmap-age-cp", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_heatmap_age_cp(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
              2: "Đau không điển hình", 3: "Không do mạch vành"}
    bins = list(range(20, 85, 5))
    labels = [f"{b}-{b+4}" for b in bins[:-1]]
    dff["age_group"] = pd.cut(dff["age"], bins=bins, labels=labels, right=False)
    dff["cp_label"] = dff["cp"].map(cp_map)
    ct = pd.crosstab(dff["cp_label"], dff["age_group"])
    fig = go.Figure(go.Heatmap(
        z=ct.values, x=ct.columns.astype(str), y=ct.index.astype(str),
        colorscale=[[0, T["neon_soft"]], [1, T["danger"]]],
        text=ct.values, texttemplate="%{text}", showscale=True,
        hovertemplate="Tuổi: %{x}<br>Đau ngực: %{y}<br>SL: %{z}<extra></extra>",
    ))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"],
                      xaxis_title="Nhóm tuổi", yaxis_title="Loại đau ngực",
                      margin=dict(t=10, b=40, l=140, r=10), height=420)
    return fig


@callback(Output("age-insights", "children"), Input("filtered-data-store", "data"))
def update_age_insights(json_data):
    if json_data is None:
        return []
    dff = pd.read_json(StringIO(json_data), orient="split")
    if len(dff) == 0:
        return [html.Li("Không có dữ liệu phù hợp bộ lọc.")]

    insights = []

    # Age comparison
    sick = dff[dff["target"] == 1]["age"]
    healthy = dff[dff["target"] == 0]["age"]
    if len(sick) > 0 and len(healthy) > 0:
        diff = sick.mean() - healthy.mean()
        insights.append(html.Li([
            html.Strong("Tuổi trung bình: "),
            f"Nhóm bệnh: {sick.mean():.1f} tuổi vs Không bệnh: {healthy.mean():.1f} tuổi "
            f"(chênh lệch {abs(diff):.1f} năm). ",
            "Nhóm bệnh có xu hướng trẻ hơn — cho thấy bệnh tim không chỉ xuất hiện ở người già."
            if diff < 0 else
            "Nhóm bệnh có xu hướng lớn tuổi hơn — tuổi tác là yếu tố nguy cơ quan trọng."
        ]))

    # Peak age group
    bins = list(range(20, 85, 5))
    labels = [f"{b}-{b+4}" for b in bins[:-1]]
    dff_temp = dff.copy()
    dff_temp["age_group"] = pd.cut(dff_temp["age"], bins=bins, labels=labels, right=False)
    grp_rate = dff_temp.groupby("age_group", observed=False)["target"].agg(["mean", "size"])
    reliable = grp_rate[grp_rate["size"] >= 20]
    if len(reliable) > 0:
        peak = reliable["mean"].idxmax()
        peak_rate = reliable.loc[peak, "mean"] * 100
        peak_n = int(reliable.loc[peak, "size"])
        insights.append(html.Li([
            html.Strong("Nhóm tuổi nguy cơ cao nhất: "),
            f"{peak} tuổi ({peak_rate:.1f}% bệnh, n={peak_n}). ",
            "Đây là nhóm cần ưu tiên sàng lọc và can thiệp sớm."
        ]))

    # Sex distribution in age
    male_median = dff[dff["sex"] == 1]["age"].median() if (dff["sex"] == 1).any() else 0
    female_median = dff[dff["sex"] == 0]["age"].median() if (dff["sex"] == 0).any() else 0
    insights.append(html.Li([
        html.Strong("Phân bố giới × tuổi: "),
        f"Tuổi trung vị Nam: {male_median:.0f}, Nữ: {female_median:.0f}. ",
        "Nữ giới trong mẫu có xu hướng lớn tuổi hơn nam giới."
        if female_median > male_median else
        "Nam giới trong mẫu có xu hướng lớn tuổi hơn."
    ]))

    # Heatmap insight
    cp_sick = dff[dff["target"] == 1]["cp"].value_counts()
    if len(cp_sick) > 0:
        cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
                  2: "Đau không điển hình", 3: "Không do mạch vành"}
        top_cp = cp_map.get(cp_sick.index[0], "?")
        insights.append(html.Li([
            html.Strong("Đau ngực & nhóm tuổi: "),
            f"Loại đau ngực phổ biến nhất ở nhóm bệnh: '{top_cp}'. ",
            "Mối liên hệ giữa loại đau ngực và nhóm tuổi cho thấy triệu chứng thay đổi theo độ tuổi."
        ]))

    return insights
