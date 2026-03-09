"""Page 1 — Tổng Quan Hồ Sơ Bệnh Án (Executive Health KPIs)"""
import dash
from dash import html, dcc, callback, Input, Output
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from components.theme import get_theme

dash.register_page(__name__, path="/", name="Tổng Quan KPI", order=0)

I = lambda name, sz=20, cls="": DashIconify(icon=name, width=sz, className=cls)

# ── Helpers ──
def _card(icon, icon_color, label, value_id=None, value="—", sub=""):
    """Reusable KPI card with Tailwind styling."""
    return html.Div(
        className=(
            "relative bg-card border border-neonbrd/30 rounded-xl p-5 "
            "hover:-translate-y-0.5 hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] "
            "hover:border-neonbrd transition-all duration-200 overflow-hidden"
        ),
        children=[
            html.Div(className="flex items-start justify-between", children=[
                html.Div([
                    html.P(label, className="text-xs font-medium text-txtsec uppercase tracking-wide mb-2"),
                    html.P(value, className="text-3xl font-bold text-txtpri leading-none"),
                    html.P(sub, className="text-xs text-txtsec mt-1.5") if sub else None,
                ]),
                html.Div(
                    I(icon, 28, f"text-{icon_color} opacity-70"),
                    className=f"p-2 rounded-lg bg-{icon_color}/10",
                ),
            ]),
        ],
    )


# ── Layout ──
layout = html.Div([
    html.Div(className="mb-7", children=[
        html.Div(className="flex items-center gap-3 mb-1", children=[
            I("lucide:layout-dashboard", 28, "text-neon"),
            html.H1("Tổng Quan Hồ Sơ Bệnh Án",
                     className="text-2xl font-extrabold text-txtpri tracking-tight"),
        ]),
        html.P("Executive Health KPIs — Cái nhìn tức thời về quần thể bệnh nhân",
               className="text-sm text-txtsec"),
    ]),
    html.Div(id="kpi-cards-row",
             className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-7"),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        html.Div(className="bg-card border border-neonbrd/30 rounded-xl p-5 hover:border-neonbrd hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all", children=[
            html.Div(className="flex items-center gap-2 mb-1", children=[
                I("lucide:pie-chart", 18, "text-neon"),
                html.H3("Phân bố Giới tính", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Tỷ lệ Nam / Nữ trong mẫu", className="text-xs text-txtsec mb-4"),
            dcc.Graph(id="donut-sex", config={"displayModeBar": False}),
        ]),
        html.Div(className="bg-card border border-neonbrd/30 rounded-xl p-5 hover:border-neonbrd hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all", children=[
            html.Div(className="flex items-center gap-2 mb-1", children=[
                I("lucide:git-branch", 18, "text-neon"),
                html.H3("Mức Thu Hẹp Mạch Vành (ca)", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Số lượng mạch máu chính bị tắc nghẽn (0-3)", className="text-xs text-txtsec mb-4"),
            dcc.Graph(id="bar-ca", config={"displayModeBar": False}),
        ]),
    ]),
    html.Div(className="grid grid-cols-1 gap-5 mb-5", children=[
        html.Div(className="bg-card border border-neonbrd/30 rounded-xl p-5 hover:border-neonbrd hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all", children=[
            html.Div(className="flex items-center gap-2 mb-1", children=[
                I("lucide:heart-pulse", 18, "text-neon"),
                html.H3("Phân bố Chẩn đoán Bệnh Tim", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("Tỷ lệ bệnh nhân có bệnh và không bệnh", className="text-xs text-txtsec mb-4"),
            dcc.Graph(id="donut-target", config={"displayModeBar": False}),
        ]),
        html.Div(className="bg-card border border-neonbrd/30 rounded-xl p-5 hover:border-neonbrd hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all", children=[
            html.Div(className="flex items-center gap-2 mb-1", children=[
                I("lucide:bar-chart-3", 18, "text-neon"),
                html.H3("Phân bố Loại Đau Ngực", className="text-sm font-semibold text-txtpri"),
            ]),
            html.P("4 nhóm triệu chứng đau ngực (cp)", className="text-xs text-txtsec mb-4"),
            dcc.Graph(id="bar-cp", config={"displayModeBar": False}),
        ]),
    ]),
    # ── Insight Panel ──
    html.Div(
        className="bg-neonsoft/20 border border-neon/30 rounded-xl p-5",
        children=[
            html.Div(className="flex items-center gap-2 mb-3", children=[
                I("lucide:lightbulb", 18, "text-warning"),
                html.H3("Nhận Xét & Insight — Tổng Quan", className="text-sm font-semibold text-txtpri"),
            ]),
            html.Ul(id="overview-insights", className="space-y-2 text-sm text-txtsec list-disc list-inside leading-relaxed"),
        ],
    ),
])


# ── Callbacks ──
@callback(Output("kpi-cards-row", "children"), Input("filtered-data-store", "data"))
def update_kpis(json_data):
    if json_data is None:
        return []
    dff = pd.read_json(StringIO(json_data), orient="split")
    total = len(dff)
    risk_pct = (dff["target"].sum() / total * 100) if total else 0
    avg_age = dff["age"].mean() if total else 0
    avg_chol = dff["chol"].mean() if total else 0
    return [
        _card("lucide:users", "neon", "Tổng bệnh nhân",
              value=f"{total:,}", sub="Trong bộ lọc hiện tại"),
        _card("lucide:heart-crack", "danger", "Tỷ lệ nguy cơ",
              value=f"{risk_pct:.1f}%", sub=f"{int(dff['target'].sum())} bệnh nhân có bệnh tim"),
        _card("lucide:calendar-clock", "warning", "Tuổi trung bình",
              value=f"{avg_age:.1f}", sub="Năm tuổi"),
        _card("lucide:droplets", "success", "Cholesterol TB",
              value=f"{avg_chol:.0f}", sub="mg/dl"),
    ]


@callback(Output("donut-sex", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_donut_sex(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    counts = dff["sex"].value_counts().sort_index()
    fig = go.Figure(go.Pie(
        labels=["Nữ giới", "Nam giới"],
        values=[counts.get(0, 0), counts.get(1, 0)],
        hole=0.55, marker_colors=[T["primary"], T["danger"]],
        textinfo="label+percent", textfont_size=13,
        hovertemplate="<b>%{label}</b><br>%{value} bệnh nhân<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"], showlegend=False,
                      margin=dict(t=10, b=10, l=10, r=10), height=400)
    return fig


@callback(Output("bar-ca", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_bar_ca(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    counts = dff["ca"].value_counts().sort_index()
    fig = go.Figure(go.Bar(
        x=[f"{int(k)} mạch" for k in counts.index], y=counts.values,
        marker_color=T["bar_colors"][:len(counts)],
        text=counts.values, textposition="auto",
        hovertemplate="Mạch tắc: %{x}<br>Bệnh nhân: %{y}<extra></extra>",
    ))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"],
                      xaxis_title="Số mạch tắc nghẽn", yaxis_title="Số bệnh nhân",
                      margin=dict(t=10, b=40, l=50, r=10), height=400,
                      xaxis=dict(gridcolor=T["grid_color"]),
                      yaxis=dict(gridcolor=T["grid_color"]))
    return fig


@callback(Output("donut-target", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_donut_target(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    counts = dff["target"].value_counts().sort_index()
    fig = go.Figure(go.Pie(
        labels=["Không bệnh tim", "Có bệnh tim"],
        values=[counts.get(0, 0), counts.get(1, 0)],
        hole=0.55, marker_colors=[T["success"], T["danger"]],
        textinfo="label+percent", textfont_size=13,
        hovertemplate="<b>%{label}</b><br>%{value} bệnh nhân<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"], showlegend=False,
                      margin=dict(t=10, b=10, l=10, r=10), height=400)
    return fig


@callback(Output("bar-cp", "figure"),
          [Input("filtered-data-store", "data"), Input("theme-store", "data")])
def update_bar_cp(json_data, theme):
    T = get_theme(theme)
    if json_data is None:
        return go.Figure()
    dff = pd.read_json(StringIO(json_data), orient="split")
    cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
              2: "Đau không điển hình", 3: "Không do mạch vành"}
    dff["cp_label"] = dff["cp"].map(cp_map)
    counts = dff["cp_label"].value_counts()
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker_color=T["bar_colors"][:len(counts)],
        text=counts.values, textposition="auto",
        hovertemplate="<b>%{x}</b><br>Bệnh nhân: %{y}<extra></extra>",
    ))
    fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                      font_color=T["font_color"],
                      xaxis_title="Loại đau ngực", yaxis_title="Số bệnh nhân",
                      margin=dict(t=10, b=40, l=50, r=10), height=400,
                      xaxis=dict(gridcolor=T["grid_color"]),
                      yaxis=dict(gridcolor=T["grid_color"]))
    return fig


@callback(Output("overview-insights", "children"),
          Input("filtered-data-store", "data"))
def update_overview_insights(json_data):
    if json_data is None:
        return []
    dff = pd.read_json(StringIO(json_data), orient="split")
    total = len(dff)
    if total == 0:
        return [html.Li("Không có dữ liệu phù hợp bộ lọc.")]

    insights = []
    risk_pct = dff["target"].mean() * 100
    n_male = (dff["sex"] == 1).sum()
    male_pct = n_male / total * 100

    insights.append(html.Li([
        html.Strong("Tỷ lệ bệnh: "),
        f"{risk_pct:.1f}% bệnh nhân trong bộ lọc được chẩn đoán có bệnh tim. ",
        "Tỷ lệ cao cho thấy mẫu nghiêng về nhóm có nguy cơ." if risk_pct > 50
        else "Tỷ lệ cho thấy phân bố khá cân bằng." if risk_pct > 40
        else "Nhóm không bệnh chiếm đa số."
    ]))
    insights.append(html.Li([
        html.Strong("Giới tính: "),
        f"Nam giới chiếm {male_pct:.1f}% ({n_male}/{total}). ",
        "Dataset thiên lệch về nam giới — kết quả cần diễn giải cẩn thận cho nữ giới."
        if male_pct > 60 else "Phân bố giới tính tương đối cân bằng."
    ]))

    # CP insight
    cp_mode = dff["cp"].mode()
    if len(cp_mode) > 0:
        cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
                  2: "Đau không điển hình", 3: "Không do mạch vành"}
        most_common = cp_map.get(cp_mode.iloc[0], "?")
        insights.append(html.Li([
            html.Strong("Đau ngực: "),
            f"Nhóm '{most_common}' chiếm tỷ lệ cao nhất. ",
            "Đáng lưu ý: nhiều bệnh nhân có bệnh tim lại không có triệu chứng đau ngực điển hình."
        ]))

    # CA insight
    ca_nonzero = (dff["ca"] > 0).mean() * 100
    insights.append(html.Li([
        html.Strong("Mạch tắc: "),
        f"{ca_nonzero:.1f}% bệnh nhân có ≥ 1 mạch vành bị tắc. ",
        "Đây là yếu tố tiên lượng mạnh cho bệnh tim."
    ]))

    avg_age = dff["age"].mean()
    insights.append(html.Li([
        html.Strong("Tuổi trung bình: "),
        f"{avg_age:.1f} tuổi — phần lớn bệnh nhân ở lứa tuổi trung niên, phù hợp với đối tượng nguy cơ cao."
    ]))

    return insights
