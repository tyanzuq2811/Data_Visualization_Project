"""
export_charts.py — Xuất tất cả biểu đồ chính ra ảnh PNG cho slide thuyết trình.
Chạy: python export_charts.py
Kết quả: thư mục exports/ chứa ~20 ảnh PNG (nền trắng, chữ đậm, slide-ready).
"""
import os, sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "exports")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(os.path.join(BASE, "heart.csv"))
df.columns = df.columns.str.strip()
df = df.drop_duplicates().reset_index(drop=True)

# ── Slide-friendly theme (nền trắng, chữ đậm) ──
T = {
    "paper_bg":   "#ffffff",
    "plot_bg":    "#fafcff",
    "font_color": "#1a1a2e",
    "grid_color": "rgba(0, 100, 200, 0.08)",
    "primary":    "#0066cc",
    "danger":     "#dc2626",
    "success":    "#16a34a",
    "warning":    "#d97706",
    "neon":       "#0066cc",
    "neon_soft":  "rgba(0,100,200,0.08)",
    "bar_colors": ["#0066cc", "#16a34a", "#dc2626", "#d97706",
                   "#7c3aed", "#0891b2", "#db2777", "#ca8a04"],
}

W, H = 1200, 600  # slide aspect ratio
FONT = dict(family="Inter, Arial, sans-serif", size=14, color=T["font_color"])
MARGIN = dict(t=60, b=60, l=70, r=30)

def _layout(**kw):
    """Common layout settings for all exported charts."""
    base = dict(
        paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
        font=FONT, margin=MARGIN, width=W, height=H,
    )
    base.update(kw)
    return base

def save(fig, name):
    path = os.path.join(OUT, f"{name}.png")
    fig.write_image(path, scale=2)
    print(f"  ✓ {name}.png")

# ==================================================================
print("═══ PAGE 0: EDA ═══")
# ==================================================================

# 0-1 Missing values
missing_counts = df.isnull().sum()
missing_pct = (df.isnull().mean() * 100).round(2)
fig = go.Figure(go.Bar(
    x=missing_counts.index, y=missing_counts.values,
    marker_color=[T["danger"] if v > 0 else T["success"] for v in missing_counts.values],
    text=[f"{v} ({p:.1f}%)" for v, p in zip(missing_counts.values, missing_pct.values)],
    textposition="auto", textfont=dict(size=13),
))
fig.add_annotation(
    x=0.5, y=0.5, xref="paper", yref="paper",
    text="✅ Không có giá trị thiếu (Missing = 0)",
    showarrow=False, font=dict(size=20, color=T["success"]),
)
fig.update_layout(**_layout(
    title="Phân Tích Giá Trị Thiếu (Missing Values)",
    xaxis_title="Biến", yaxis_title="Số lượng Missing",
    xaxis=dict(tickangle=-45, gridcolor=T["grid_color"]),
    yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p0_missing_values")

# 0-2 Outlier bar
numeric_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
col_labels = {"age": "Tuổi", "trestbps": "Huyết áp", "chol": "Cholesterol",
              "thalach": "Nhịp tim max", "oldpeak": "ST chênh"}
col_units = {"age": "tuổi", "trestbps": "mmHg", "chol": "mg/dl",
             "thalach": "bpm", "oldpeak": "mm"}

outlier_info = {}
for col in numeric_cols:
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    lo, up = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n = int(((df[col] < lo) | (df[col] > up)).sum())
    outlier_info[col] = {"n": n, "lo": lo, "up": up, "pct": n / len(df) * 100}

fig = go.Figure(go.Bar(
    x=[col_labels[c] for c in numeric_cols],
    y=[outlier_info[c]["n"] for c in numeric_cols],
    marker_color=[T["danger"] if outlier_info[c]["n"] > 0 else T["success"] for c in numeric_cols],
    text=[f"<b>{outlier_info[c]['n']}</b> ({outlier_info[c]['pct']:.1f}%)" for c in numeric_cols],
    textposition="auto", textfont=dict(size=14),
))
fig.update_layout(**_layout(
    title="Số Lượng Outlier Theo Biến (IQR Method)",
    xaxis_title="Biến", yaxis_title="Số outlier",
    xaxis=dict(gridcolor=T["grid_color"]),
    yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p0_outlier_bar")

# 0-3 Outlier boxplot subplots
fig = make_subplots(rows=1, cols=5,
    subplot_titles=[f"{col_labels[c]} ({col_units[c]})" for c in numeric_cols],
    horizontal_spacing=0.06)
for i, col in enumerate(numeric_cols):
    info = outlier_info[col]
    fig.add_trace(go.Box(
        y=df[col], name=col_labels[col], marker_color=T["bar_colors"][i],
        boxpoints="outliers", boxmean="sd",
    ), row=1, col=i+1)
    for bound, lbl in [(info["lo"], "Lower"), (info["up"], "Upper")]:
        fig.add_hline(y=bound, line_dash="dot", line_color=T["warning"], line_width=1.5,
                      row=1, col=i+1)
fig.update_layout(paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"],
                  font=FONT, showlegend=False, width=1400, height=500,
                  title="Boxplot Chi Tiết Outlier — Từng Biến Riêng Biệt",
                  margin=dict(t=60, b=30, l=40, r=20))
save(fig, "p0_outlier_boxplots")

# 0-4 Target distribution
target_counts = df["target"].value_counts().sort_index()
fig = go.Figure(go.Bar(
    x=["Không bệnh (0)", "Có bệnh (1)"],
    y=[target_counts.get(0, 0), target_counts.get(1, 0)],
    marker_color=[T["success"], T["danger"]],
    text=[target_counts.get(0, 0), target_counts.get(1, 0)],
    textposition="auto", textfont=dict(size=16),
))
fig.update_layout(**_layout(
    title="Phân Phối Biến Mục Tiêu (Target Distribution)",
    yaxis_title="Số bệnh nhân",
    xaxis=dict(gridcolor=T["grid_color"]),
    yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p0_target_distribution")

# ==================================================================
print("═══ PAGE 1: TỔNG QUAN KPI ═══")
# ==================================================================

# 1-1 Donut giới tính
counts = df["sex"].value_counts().sort_index()
fig = go.Figure(go.Pie(
    labels=["Nữ giới", "Nam giới"], values=[counts.get(0, 0), counts.get(1, 0)],
    hole=0.55, marker_colors=[T["primary"], T["danger"]],
    textinfo="label+percent", textfont_size=15,
))
fig.update_layout(**_layout(title="Phân Bố Giới Tính", showlegend=False))
save(fig, "p1_donut_sex")

# 1-2 Bar CA
counts = df["ca"].value_counts().sort_index()
fig = go.Figure(go.Bar(
    x=[f"{int(k)} mạch" for k in counts.index], y=counts.values,
    marker_color=T["bar_colors"][:len(counts)],
    text=counts.values, textposition="auto", textfont=dict(size=14),
))
fig.update_layout(**_layout(
    title="Mức Thu Hẹp Mạch Vành (ca)",
    xaxis_title="Số mạch tắc nghẽn", yaxis_title="Số bệnh nhân",
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p1_bar_ca")

# 1-3 Donut Target
counts = df["target"].value_counts().sort_index()
fig = go.Figure(go.Pie(
    labels=["Không bệnh tim", "Có bệnh tim"],
    values=[counts.get(0, 0), counts.get(1, 0)],
    hole=0.55, marker_colors=[T["success"], T["danger"]],
    textinfo="label+percent", textfont_size=15,
))
fig.update_layout(**_layout(title="Phân Bố Chẩn Đoán Bệnh Tim", showlegend=False))
save(fig, "p1_donut_target")

# 1-4 Bar CP
cp_map = {0: "Không triệu chứng", 1: "Đau điển hình",
          2: "Đau không điển hình", 3: "Không do mạch vành"}
df_temp = df.copy()
df_temp["cp_label"] = df_temp["cp"].map(cp_map)
counts = df_temp["cp_label"].value_counts()
fig = go.Figure(go.Bar(
    x=counts.index, y=counts.values,
    marker_color=T["bar_colors"][:len(counts)],
    text=counts.values, textposition="auto", textfont=dict(size=14),
))
fig.update_layout(**_layout(
    title="Phân Bố Loại Đau Ngực (cp)",
    xaxis_title="Loại đau ngực", yaxis_title="Số bệnh nhân",
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p1_bar_cp")

# ==================================================================
print("═══ PAGE 2: XU HƯỚNG TUỔI ═══")
# ==================================================================

# 2-1 Line + Bar Age Trend
bins = list(range(20, 85, 5))
labels = [f"{b}-{b+4}" for b in bins[:-1]]
df_temp = df.copy()
df_temp["age_group"] = pd.cut(df_temp["age"], bins=bins, labels=labels, right=False)
grp = df_temp.groupby("age_group", observed=False)["target"]
rate = (grp.mean() * 100).round(1)
cnt = grp.size()
sick = grp.sum().astype(int)
MIN_SAMPLE = 20

fig = go.Figure()
bar_c = [T["primary"] if n >= MIN_SAMPLE else "rgba(150,150,150,0.35)" for n in cnt.values]
fig.add_trace(go.Bar(x=rate.index.astype(str), y=cnt.values, name="Tổng BN",
    marker_color=bar_c, opacity=0.5, text=[f"{n}" for n in cnt.values], textposition="auto"))
fig.add_trace(go.Bar(x=rate.index.astype(str), y=sick.values, name="Có bệnh tim",
    marker_color=T["danger"], opacity=0.55, text=[f"{s}" for s in sick.values], textposition="inside"))
mk_sizes = [11 if n >= MIN_SAMPLE else 7 for n in cnt.values]
mk_colors = [T["danger"] if n >= MIN_SAMPLE else "rgba(150,150,150,0.7)" for n in cnt.values]
fig.add_trace(go.Scatter(
    x=rate.index.astype(str), y=rate.values, name="Tỷ lệ bệnh %",
    mode="lines+markers+text", line=dict(color=T["danger"], width=3),
    marker=dict(size=mk_sizes, color=mk_colors, line=dict(width=2, color="#1a1a2e")),
    text=[f"{r:.0f}%" for r in rate.values], textposition="top center", textfont=dict(size=11),
    yaxis="y2",
))
fig.update_layout(
    **_layout(title="Tỷ Lệ Bệnh Tim Theo Nhóm Tuổi", barmode="overlay", height=550),
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(title="Nhóm tuổi", gridcolor=T["grid_color"]),
    yaxis=dict(title="Số bệnh nhân", gridcolor=T["grid_color"]),
    yaxis2=dict(title="Tỷ lệ bệnh (%)", overlaying="y", side="right",
                gridcolor="rgba(0,0,0,0)", range=[0, 115]),
)
save(fig, "p2_age_trend")

# 2-2 Box Age
fig = go.Figure()
for val, label, color in [(0, "Không bệnh tim", T["success"]), (1, "Có bệnh tim", T["danger"])]:
    sub = df[df["target"] == val]
    fig.add_trace(go.Box(y=sub["age"], name=label, marker_color=color, boxmean="sd"))
fig.update_layout(**_layout(
    title="Box-Plot Tuổi vs Chẩn Đoán",
    yaxis_title="Tuổi",
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p2_box_age")

# 2-3 Histogram Age by Sex
fig = go.Figure()
for val, label, color in [(0, "Nữ giới", T["primary"]), (1, "Nam giới", T["danger"])]:
    sub = df[df["sex"] == val]
    fig.add_trace(go.Histogram(x=sub["age"], name=label, marker_color=color, opacity=0.7, nbinsx=15))
fig.update_layout(**_layout(
    title="Histogram Tuổi Theo Giới Tính", barmode="overlay",
    xaxis_title="Tuổi", yaxis_title="Số bệnh nhân",
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p2_hist_age_sex")

# 2-4 Heatmap Age × CP
df_temp = df.copy()
df_temp["age_group"] = pd.cut(df_temp["age"], bins=bins, labels=labels, right=False)
df_temp["cp_label"] = df_temp["cp"].map(cp_map)
ct = pd.crosstab(df_temp["cp_label"], df_temp["age_group"])
fig = go.Figure(go.Heatmap(
    z=ct.values, x=ct.columns.astype(str), y=ct.index.astype(str),
    colorscale=[[0, "#e8f4ff"], [1, T["danger"]]],
    text=ct.values, texttemplate="%{text}", showscale=True,
))
fig.update_layout(**_layout(
    title="Heatmap Nhóm Tuổi × Loại Đau Ngực",
    xaxis_title="Nhóm tuổi", yaxis_title="Loại đau ngực",
    margin=dict(t=60, b=50, l=160, r=30),
))
save(fig, "p2_heatmap_age_cp")

# ==================================================================
print("═══ PAGE 3: LÂM SÀNG ═══")
# ==================================================================

def make_hist_threshold(col, threshold, unit, col_label, flip=False):
    fig = go.Figure()
    for val, label, color in [(0, "Không bệnh tim", T["success"]), (1, "Có bệnh tim", T["danger"])]:
        sub = df[df["target"] == val]
        fig.add_trace(go.Histogram(x=sub[col], name=label, marker_color=color, opacity=0.6, nbinsx=25))
    fig.add_vline(x=threshold, line_dash="dash", line_color=T["warning"], line_width=2.5)
    fig.add_annotation(x=threshold, y=1.06, yref="paper", showarrow=False,
        text=f"⚠ Ngưỡng {threshold} {unit}", font=dict(size=13, color=T["warning"]))
    for val, label, color in [(0, "Không bệnh tim", T["success"]), (1, "Có bệnh tim", T["danger"])]:
        sub = df[df["target"] == val]
        bad_pct = ((sub[col] < threshold).mean() * 100) if flip else ((sub[col] > threshold).mean() * 100)
        direction = "dưới" if flip else "trên"
        fig.add_annotation(
            x=0.98 if val == 1 else 0.02, y=0.97 - val * 0.09,
            xref="paper", yref="paper", xanchor="right" if val == 1 else "left",
            showarrow=False,
            text=f"<b>{label}</b>: <b>{bad_pct:.0f}%</b> {direction} ngưỡng",
            font=dict(size=13, color=color), bgcolor="#ffffff", borderpad=4,
        )
    if flip:
        fig.add_vrect(x0=df[col].min()*0.95, x1=threshold, fillcolor=T["danger"],
                      opacity=0.06, line_width=0, annotation_text="Vùng nguy cơ",
                      annotation_position="top left",
                      annotation_font=dict(size=11, color=T["danger"]))
    else:
        fig.add_vrect(x0=threshold, x1=df[col].max()*1.05, fillcolor=T["danger"],
                      opacity=0.06, line_width=0, annotation_text="Vùng nguy cơ",
                      annotation_position="top right",
                      annotation_font=dict(size=11, color=T["danger"]))
    fig.update_layout(**_layout(
        title=f"{col_label} — Histogram + Ngưỡng Lâm Sàng", barmode="overlay",
        xaxis_title=f"{col_label} ({unit})", yaxis_title="Số bệnh nhân",
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
    ))
    return fig

save(make_hist_threshold("chol", 200, "mg/dl", "Cholesterol"), "p3_hist_chol")
save(make_hist_threshold("trestbps", 130, "mmHg", "Huyết Áp Nghỉ"), "p3_hist_bp")
save(make_hist_threshold("thalach", 140, "bpm", "Nhịp Tim Tối Đa", flip=True), "p3_hist_thalach")

# 3-4 Stacked CP
ct = pd.crosstab(df["cp"].map(cp_map), df["target"], normalize="index") * 100
fig = go.Figure()
for col_val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
    if col_val in ct.columns:
        fig.add_trace(go.Bar(y=ct.index, x=ct[col_val], name=label, orientation="h",
            marker_color=color, text=ct[col_val].round(1).astype(str) + "%", textposition="inside"))
fig.update_layout(**_layout(
    title="Nghịch Lý Đau Ngực — Stacked 100%", barmode="stack",
    xaxis_title="Tỷ lệ %", margin=dict(t=60, b=50, l=180, r=30),
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(gridcolor=T["grid_color"], range=[0, 100]),
    yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p3_stacked_cp")

# 3-5 Grouped FBS
ct = pd.crosstab(df["fbs"], df["target"])
fig = go.Figure()
for col_val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
    if col_val in ct.columns:
        fig.add_trace(go.Bar(
            x=["FBS ≤ 120" if i == 0 else "FBS > 120" for i in ct.index],
            y=ct[col_val], name=label, marker_color=color,
            text=ct[col_val], textposition="auto", textfont=dict(size=14),
        ))
fig.update_layout(**_layout(
    title="Đường Huyết Lúc Đói (fbs) — Grouped Bar", barmode="group",
    yaxis_title="Số bệnh nhân",
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p3_grouped_fbs")

# 3-6 Grouped RestECG
ecg_map = {0: "Bình thường", 1: "Bất thường ST-T", 2: "Dày thất trái"}
ct = pd.crosstab(df["restecg"], df["target"])
fig = go.Figure()
for col_val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
    if col_val in ct.columns:
        fig.add_trace(go.Bar(
            x=[ecg_map.get(i, str(i)) for i in ct.index],
            y=ct[col_val], name=label, marker_color=color,
            text=ct[col_val], textposition="auto", textfont=dict(size=14),
        ))
fig.update_layout(**_layout(
    title="Điện Tâm Đồ (restecg) — Grouped Bar", barmode="group",
    yaxis_title="Số bệnh nhân",
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p3_grouped_ecg")

# ==================================================================
print("═══ PAGE 4: TƯƠNG QUAN ═══")
# ==================================================================

# 4-1 Correlation heatmap
FEATURE_NAMES_VI = {
    "age": "Tuổi", "sex": "Giới tính", "cp": "Đau ngực",
    "trestbps": "Huyết áp nghỉ", "chol": "Cholesterol",
    "fbs": "Đường huyết", "restecg": "Điện tâm đồ",
    "thalach": "Nhịp tim max", "exang": "Đau khi vận động",
    "oldpeak": "ST chênh", "slope": "Slope ST",
    "ca": "Mạch tắc (ca)", "thal": "Thalassemia", "target": "Bệnh tim",
}
corr = df.corr(numeric_only=True).round(2)
lab = [FEATURE_NAMES_VI.get(c, c) for c in corr.columns]
fig = go.Figure(go.Heatmap(
    z=corr.values, x=lab, y=lab,
    colorscale=[[0, "#dc2626"], [0.5, "#ffffff"], [1, "#0066cc"]],
    zmin=-1, zmax=1, text=corr.values, texttemplate="%{text}",
))
fig.update_layout(
    paper_bgcolor=T["paper_bg"], plot_bgcolor=T["plot_bg"], font=FONT,
    title="Ma Trận Tương Quan Pearson",
    width=900, height=800, margin=dict(t=60, b=80, l=130, r=30),
    xaxis_tickangle=-45,
)
save(fig, "p4_corr_heatmap")

# 4-2 Feature importance
corr_target = df.corr(numeric_only=True)["target"].drop("target").abs().sort_values()
lab2 = [FEATURE_NAMES_VI.get(c, c) for c in corr_target.index]
colors = [T["danger"] if v > 0.3 else T["warning"] if v > 0.15 else "#a0c4e8" for v in corr_target.values]
fig = go.Figure(go.Bar(
    y=lab2, x=corr_target.values, orientation="h", marker_color=colors,
    text=corr_target.values.round(3), textposition="outside", textfont=dict(size=13),
))
fig.update_layout(**_layout(
    title="Feature Importance — |r| với Target",
    xaxis_title="|Pearson r|", margin=dict(t=60, b=50, l=140, r=60),
    xaxis=dict(gridcolor=T["grid_color"], range=[0, corr_target.max() * 1.2]),
    yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p4_feature_importance")

# 4-3 Scatter Age × Thalach
np.random.seed(42)
fig = go.Figure()
for val, label, color in [(0, "Không bệnh", T["success"]), (1, "Có bệnh", T["danger"])]:
    sub = df[df["target"] == val]
    fig.add_trace(go.Scatter(x=sub["age"], y=sub["thalach"], mode="markers", name=label,
        marker=dict(color=color, size=7, opacity=0.6)))
    z = np.polyfit(sub["age"], sub["thalach"], 1)
    p = np.poly1d(z)
    xs = np.linspace(sub["age"].min(), sub["age"].max(), 50)
    fig.add_trace(go.Scatter(x=xs, y=p(xs), mode="lines", name=f"Trend {label}",
        line=dict(color=color, width=2, dash="dash"), showlegend=False))
fig.update_layout(**_layout(
    title="Tuổi × Nhịp Tim Tối Đa — Scatter + Trendline",
    xaxis_title="Tuổi", yaxis_title="Nhịp tim max (bpm)",
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
))
save(fig, "p4_scatter_age_thalach")

# ==================================================================
print("═══ PAGE 5: CẢNH BÁO ═══")
# ==================================================================

# 5-1 Waterfall example (patient 0)
THRESHOLDS = {"chol": 200, "trestbps": 130, "thalach": 140,
              "oldpeak": 1.5, "fbs": 1, "exang": 1, "ca": 0}

def compute_factors(row):
    f = []
    if row["chol"] > 200: f.append("Cholesterol cao")
    if row["trestbps"] > 130: f.append("Huyết áp cao")
    if row["thalach"] < 140: f.append("Nhịp tim thấp")
    if row["oldpeak"] > 1.5: f.append("ST chênh cao")
    if row["fbs"] == 1: f.append("Đường huyết cao")
    if row["exang"] == 1: f.append("Đau khi vận động")
    if row["ca"] > 0: f.append(f"Mạch tắc ({int(row['ca'])})")
    if row["cp"] == 0: f.append("Thiếu máu thầm lặng")
    return f

row = df.iloc[0]
factors = compute_factors(row)
wf_names = factors + ["Tổng"]
wf_values = [1] * len(factors) + [len(factors)]
wf_measures = ["relative"] * len(factors) + ["total"]
sev_color = "#e74c3c" if len(factors) >= 5 else "#f39c12" if len(factors) >= 3 else "#27ae60"
fig = go.Figure(go.Waterfall(
    x=wf_names, y=wf_values, measure=wf_measures,
    connector_line_color="rgba(0,0,0,0)",
    increasing_marker_color=T["danger"],
    totals_marker_color=sev_color,
    textposition="outside", text=["+1"] * len(factors) + [str(len(factors))],
    textfont=dict(size=14),
))
fig.update_layout(**_layout(
    title=f"Waterfall — Tích Lũy Nguy Cơ (Bệnh nhân #0)",
    xaxis_tickangle=-20, yaxis_title="Điểm tích lũy",
    xaxis=dict(gridcolor=T["grid_color"]), yaxis=dict(gridcolor=T["grid_color"]),
    height=500,
))
save(fig, "p5_waterfall_example")

# ==================================================================
print(f"\n✅ HOÀN TẤT — Tất cả ảnh đã lưu vào: {OUT}")
print(f"   Tổng: {len(os.listdir(OUT))} file PNG")
