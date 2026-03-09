"""Page 4 — Tương Quan & Feature Importance (Correlation Matrix)"""
import dash, numpy as np
from dash import html, dcc, callback, Input, Output
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from components.theme import get_theme

dash.register_page(__name__, path="/correlation", name="Tương Quan", order=3)

I = lambda name, sz=20, cls="": DashIconify(icon=name, width=sz, className=cls)

FEATURE_NAMES_VI = {
    "age": "Tuổi", "sex": "Giới tính", "cp": "Đau ngực",
    "trestbps": "Huyết áp nghỉ", "chol": "Cholesterol",
    "fbs": "Đường huyết", "restecg": "Điện tâm đồ",
    "thalach": "Nhịp tim max", "exang": "Đau khi vận động",
    "oldpeak": "ST chênh", "slope": "Slope ST",
    "ca": "Mạch tắc (ca)", "thal": "Thalassemia", "target": "Bệnh tim",
}


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
            I("lucide:scatter-chart", 28, "text-neon"),
            html.H1("Tương Quan & Feature Importance",
                     className="text-2xl font-extrabold text-txtpri tracking-tight"),
        ]),
        html.P("Correlation Matrix — Khám phá mối quan hệ giữa các đặc trưng",
               className="text-sm text-txtsec"),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        _chart_card("lucide:grid-3x3", "Ma Trận Tương Quan Pearson",
                     "Hệ số tương quan giữa tất cả cặp biến", "corr-heatmap"),
        _chart_card("lucide:trophy", "Feature Importance (|r| với target)",
                     "Xếp hạng ảnh hưởng của từng biến đến bệnh tim", "feature-imp"),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        _chart_card("lucide:move-diagonal", "Tuổi × Nhịp Tim Max",
                     "Scatter + trend-line theo nhóm bệnh", "scatter-age-thalach"),
        _chart_card("lucide:move-diagonal", "Oldpeak × Đau Khi Vận Động",
                     "Scatter + jitter (exang categorical)", "scatter-oldpeak"),
        _chart_card("lucide:move-diagonal", "CA × Oldpeak",
                     "Mối quan hệ mạch tắc & ST chênh", "scatter-ca-oldpeak"),
    ]),
    # ── Insight Panel ──
    html.Div(
        className="bg-neonsoft/20 border border-neon/30 rounded-xl p-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:lightbulb", 18, "text-warning"),
                html.H3("Nhận Xét & Insight — Tương Quan", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Ul(id="corr-insights", className="space-y-2 text-sm text-txtsec list-disc list-inside leading-relaxed"),
        ],
    ),
])


@callback(Output("corr-heatmap", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_heatmap(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    corr = dff.corr(numeric_only=True).round(2)
    labels = [FEATURE_NAMES_VI.get(c, c) for c in corr.columns]
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=labels, y=labels,
        colorscale=[[0, "#ff3366"], [0.5, T["paper_bg"]], [1, "#00d4ff"]],
        zmin=-1, zmax=1, text=corr.values, texttemplate="%{text}",
        hovertemplate="%{x} × %{y}: %{z}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        margin=dict(t=10, b=60, l=100, r=10), height=450,
        xaxis_tickangle=-45,
    )
    return fig


@callback(Output("feature-imp", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_feature_importance(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    corr_target = dff.corr(numeric_only=True)["target"].drop("target").abs().sort_values()
    labels = [FEATURE_NAMES_VI.get(c, c) for c in corr_target.index]
    colors = [T["danger"] if v > 0.3 else T["warning"] if v > 0.15 else T["neon_soft"]
              for v in corr_target.values]
    fig = go.Figure(go.Bar(
        y=labels, x=corr_target.values, orientation="h",
        marker_color=colors,
        text=corr_target.values.round(3), textposition="outside",
        hovertemplate="<b>%{y}</b>: |r| = %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        xaxis_title="|Pearson r|", margin=dict(t=10, b=40, l=120, r=50), height=450,
        xaxis=dict(gridcolor=T["grid_color"], range=[0, corr_target.max() * 1.2]),
        yaxis=dict(gridcolor=T["grid_color"]),
    )
    return fig


@callback(Output("scatter-age-thalach", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_scatter_age_thalach(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    fig = go.Figure()
    for val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
        sub = dff[dff["target"] == val]
        fig.add_trace(go.Scatter(
            x=sub["age"], y=sub["thalach"], mode="markers", name=label,
            marker=dict(color=color, size=6, opacity=0.6),
            hovertemplate="Tuổi: %{x}<br>Nhịp tim max: %{y}<extra></extra>",
        ))
        if len(sub) > 2:
            z = np.polyfit(sub["age"], sub["thalach"], 1)
            p = np.poly1d(z)
            xs = np.linspace(sub["age"].min(), sub["age"].max(), 50)
            fig.add_trace(go.Scatter(
                x=xs, y=p(xs), mode="lines", name=f"Trend {label}",
                line=dict(color=color, width=2, dash="dash"), showlegend=False,
            ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        xaxis_title="Tuổi", yaxis_title="Nhịp tim max (bpm)",
        margin=dict(t=10, b=40, l=50, r=10), height=420,
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
    )
    return fig


@callback(Output("scatter-oldpeak", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_scatter_oldpeak(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    fig = go.Figure()
    for val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
        sub = dff[dff["target"] == val]
        jitter = np.random.normal(0, 0.08, len(sub))
        fig.add_trace(go.Scatter(
            x=sub["exang"] + jitter, y=sub["oldpeak"], mode="markers", name=label,
            marker=dict(color=color, size=6, opacity=0.55),
            hovertemplate="Exang: %{x:.0f}<br>Oldpeak: %{y}<extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        xaxis_title="Đau khi vận động (exang)", yaxis_title="ST chênh (oldpeak)",
        margin=dict(t=10, b=40, l=50, r=10), height=420,
        xaxis=dict(gridcolor=T["grid_color"], tickvals=[0, 1], ticktext=["Không", "Có"]),
        yaxis=dict(gridcolor=T["grid_color"]),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
    )
    return fig


@callback(Output("scatter-ca-oldpeak", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_scatter_ca_oldpeak(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    fig = go.Figure()
    for val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
        sub = dff[dff["target"] == val]
        jitter = np.random.normal(0, 0.1, len(sub))
        fig.add_trace(go.Scatter(
            x=sub["ca"] + jitter, y=sub["oldpeak"], mode="markers", name=label,
            marker=dict(color=color, size=6, opacity=0.55),
            hovertemplate="CA: %{x:.0f}<br>Oldpeak: %{y}<extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font_color=T["font_color"],
        xaxis_title="Số mạch tắc (ca)", yaxis_title="ST chênh (oldpeak)",
        margin=dict(t=10, b=40, l=50, r=10), height=420,
        xaxis=dict(gridcolor=T["grid_color"]),
        yaxis=dict(gridcolor=T["grid_color"]),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
    )
    return fig


@callback(Output("corr-insights", "children"),
          [Input("filtered-data-store", "data")])
def update_corr_insights(json_data):
    if json_data is None:
        return []
    dff = pd.read_json(StringIO(json_data), orient="split")
    if len(dff) < 5:
        return [html.Li("Không đủ dữ liệu để phân tích tương quan.")]

    insights = []
    corr_target = dff.corr(numeric_only=True)["target"].drop("target").abs().sort_values(ascending=False)

    # Top 3 features
    top3 = corr_target.head(3)
    names_vi = {
        "age": "tuổi", "sex": "giới tính", "cp": "đau ngực",
        "trestbps": "huyết áp nghỉ", "chol": "cholesterol",
        "fbs": "đường huyết", "restecg": "điện tâm đồ",
        "thalach": "nhịp tim max", "exang": "đau khi vận động",
        "oldpeak": "ST chênh", "slope": "slope ST",
        "ca": "mạch tắc", "thal": "thalassemia",
    }
    top_str = ", ".join([f"{names_vi.get(k, k)} (|r|={v:.3f})" for k, v in top3.items()])
    insights.append(html.Li([
        html.Strong("Top 3 biến tương quan mạnh nhất với target: "),
        top_str + ". ",
        "Đây là các yếu tố tiên lượng quan trọng nhất cho chẩn đoán bệnh tim."
    ]))

    # Multicollinearity check
    corr_all = dff.corr(numeric_only=True)
    high_corr_pairs = []
    cols = corr_all.columns
    for i_c in range(len(cols)):
        for j_c in range(i_c + 1, len(cols)):
            r = abs(corr_all.iloc[i_c, j_c])
            if r > 0.5 and cols[i_c] != "target" and cols[j_c] != "target":
                high_corr_pairs.append((cols[i_c], cols[j_c], r))

    if high_corr_pairs:
        pair_strs = [f"{names_vi.get(a, a)} × {names_vi.get(b, b)} (r={r:.2f})"
                     for a, b, r in high_corr_pairs[:3]]
        insights.append(html.Li([
            html.Strong("Đa cộng tuyến: "),
            f"Phát hiện {len(high_corr_pairs)} cặp biến có |r| > 0.5: {'; '.join(pair_strs)}. ",
            "Nếu xây dựng mô hình, cần xem xét loại bỏ hoặc kết hợp các biến này."
        ]))
    else:
        insights.append(html.Li([
            html.Strong("Đa cộng tuyến: "),
            "Không phát hiện cặp biến nào có |r| > 0.5 (ngoài target). Các biến tương đối độc lập."
        ]))

    # Scatter insight: age vs thalach
    if "age" in dff and "thalach" in dff:
        r_val = dff["age"].corr(dff["thalach"])
        insights.append(html.Li([
            html.Strong("Tuổi × Nhịp tim max: "),
            f"r = {r_val:.3f}. ",
            "Tương quan nghịch rõ rệt — tuổi càng cao, nhịp tim tối đa đạt được càng thấp."
            if r_val < -0.3 else
            "Tương quan nghịch nhẹ — xu hướng giảm nhịp tim max theo tuổi."
            if r_val < 0 else
            "Không có tương quan rõ rệt."
        ]))

    # Oldpeak insight
    if "oldpeak" in dff:
        r_oldpeak = dff["oldpeak"].corr(dff["target"])
        insights.append(html.Li([
            html.Strong("Oldpeak (ST chênh): "),
            f"r với target = {r_oldpeak:.3f}. ",
            "ST depression cao liên quan mạnh đến bệnh tim — đây là chỉ số lâm sàng then chốt."
            if abs(r_oldpeak) > 0.2 else
            "Tương quan yếu trong mẫu hiện tại."
        ]))

    return insights
