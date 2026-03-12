"""
CardioViz — Heart Disease Multi-page Dashboard
Dash application entry point.  Tailwind CSS + DashIconify edition.
"""

import os
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, page_container
import dash
from dash_iconify import DashIconify

from components.sidebar import create_sidebar

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "heart.csv")
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()          # CSV has leading spaces in some column names

# ---------------------------------------------------------------------------
# Tailwind Play CDN — loaded BEFORE the app renders
# ---------------------------------------------------------------------------
TAILWIND_CDN = (
    "https://cdn.tailwindcss.com"
)

TAILWIND_CONFIG = """
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        neon:      '#00d4ff',
        neondark:  '#009ec5',
        neonsoft:  'rgba(0,212,255,0.12)',
        neonbrd:   'rgba(0,212,255,0.25)',
        body:      '#060b18',
        card:      '#0f1729',
        sidebar:   '#0a1020',
        inputbg:   '#111b30',
        txtpri:    '#e0f2ff',
        txtsec:    '#7aa2c9',
        danger:    '#ff3366',
        dangersoft:'rgba(255,51,102,0.12)',
        success:   '#00ff88',
        successoft:'rgba(0,255,136,0.12)',
        warning:   '#ffaa00',
        warnsoft:  'rgba(255,170,0,0.12)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
}
"""

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="CardioViz — Heart Disease Dashboard",
    update_title="Đang tải...",
    external_scripts=[
        TAILWIND_CDN,
    ],
)
server = app.server

# Inject Tailwind config script into <head>
app.index_string = '''<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%css%}
        {%favicon%}
        <script src="https://cdn.tailwindcss.com"></script>
        <script>''' + TAILWIND_CONFIG + '''</script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>'''

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = html.Div(
    className="flex min-h-screen bg-body text-txtpri font-sans",
    children=[
        dcc.Store(id="filtered-data-store", storage_type="memory"),
        dcc.Store(id="theme-store", storage_type="local", data="dark"),
        html.Div(id="theme-dummy", style={"display": "none"}),
        create_sidebar(),
        html.Div(
            className="ml-[280px] flex-1 min-h-screen p-7 bg-body transition-colors duration-300",
            id="main-content",
            children=[page_container],
        ),
    ],
)

# ---------------------------------------------------------------------------
# Theme Toggle
# ---------------------------------------------------------------------------
@app.callback(
    [Output("theme-store", "data"),
     Output("theme-toggle-btn", "children")],
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current_theme):
    new_theme = "light" if current_theme == "dark" else "dark"
    if new_theme == "light":
        icon = DashIconify(icon="lucide:sun", width=18)
        return new_theme, [icon, " Light Mode"]
    else:
        icon = DashIconify(icon="lucide:moon", width=18)
        return new_theme, [icon, " Dark Mode"]


app.clientside_callback(
    """
    function(theme) {
        if (theme === "light") {
            document.body.classList.add("light-theme");
        } else {
            document.body.classList.remove("light-theme");
        }
        return "";
    }
    """,
    Output("theme-dummy", "children"),
    Input("theme-store", "data"),
)

# ---------------------------------------------------------------------------
# Master Filter
# ---------------------------------------------------------------------------
@app.callback(
    Output("filtered-data-store", "data"),
    [Input("filter-sex", "value"),
     Input("filter-age", "value"),
     Input("filter-cp", "value"),
     Input("filter-target", "value")],
)
def master_filter(sex, age_range, cp, target):
    dff = df.copy()
    if sex != "all":
        dff = dff[dff["sex"] == int(sex)]
    if age_range:
        dff = dff[(dff["age"] >= age_range[0]) & (dff["age"] <= age_range[1])]
    if cp != "all":
        dff = dff[dff["cp"] == int(cp)]
    if target != "all":
        dff = dff[dff["target"] == int(target)]
    return dff.to_json(date_format="iso", orient="split")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)
