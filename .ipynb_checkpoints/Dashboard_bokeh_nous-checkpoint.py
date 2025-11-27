import pandas as pd
import numpy as np
import math

from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Select, MultiSelect, Slider,
    Div, CheckboxGroup
)
from bokeh.layouts import row, column
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20, Spectral6
from bokeh.io import curdoc

"""
Students Performance Dashboard (Version Bokeh)
Dashboard interactif en Bokeh permettant d'analyser
les performances scolaires des étudiants aux États-Unis.

Fonctionnalités :
- KPI affichés en haut (styled via HTML)
- Score moyen par État (bar chart)
- Évolution du score moyen par État (line chart)
- Histogramme par matière
- Boxplots par matière
- Widgets interactifs : année, états, matière, genre,
  score minimum, etc.
- Visual amélioré, grands graphiques

Lancement :
    bokeh serve --show StudentsDashboardBokeh.py
"""
df = pd.read_csv("StudentsPerformance.csv")
df = df.drop(columns=["race/ethnicity"])

df["state"] = df["state"].astype(str).str.strip().str.title()

matiere = ["math score", "reading score", "writing score"]
df["score_moyen"] = df[matiere].mean(axis=1).round(2)

years = sorted(df["year"].unique())
states = sorted(df["state"].unique())
genders = list(df["gender"].unique())

source_state_avg = ColumnDataSource()
source_state_year = ColumnDataSource()
source_hist = ColumnDataSource()

select_year = Select(
    title="Année sélectionnée",
    value=str(years[0]),
    options=[str(y) for y in years]
)

select_states = MultiSelect(
    title="Sélectionner États",
    value=states[:3],  # valeurs par défaut
    options=states,
    size=6
)

select_matiere = Select(
    title="Matière pour histogramme",
    value="math score",
    options=matiere
)

slider_min_score = Slider(
    title="Score moyen minimum",
    value=10,
    start=0,
    end=100,
    step=1
)

checkbox_gender = CheckboxGroup(
    labels=genders,
    active=list(range(len(genders)))
)

kpi_style = """
    <div style='
        font-family:Segoe UI, Arial;
        font-size:20px;
        font-weight:bold;
        padding:15px;
        width:230px;
        border-radius:12px;
        color:white;
        text-align:center;
        box-shadow:0px 2px 6px rgba(0,0,0,0.15);
    '>
        {}
    </div>
"""

kpi1 = Div(text=kpi_style.format("Score moyen global : ..."), width=250)
kpi2 = Div(text=kpi_style.format("Score max : ..."), width=250)
kpi3 = Div(text=kpi_style.format("Score min : ..."), width=250)
kpi4 = Div(text=kpi_style.format("Échantillon filtré : ..."), width=250)

def update_kpi(filtered):
    kpi1.text = kpi_style.format(f"Score moyen global<br>{filtered['score_moyen'].mean():.2f}").replace("color:white", "background:#3366CC;color:white")
    kpi2.text = kpi_style.format(f"Score max<br>{filtered['score_moyen'].max():.2f}").replace("color:white", "background:#2E8B57;color:white")
    kpi3.text = kpi_style.format(f"Score min<br>{filtered['score_moyen'].min():.2f}").replace("color:white", "background:#B22222;color:white")
    kpi4.text = kpi_style.format(f"Échantillon filtré<br>{len(filtered)}").replace("color:white", "background:#6A5ACD;color:white")

p1 = figure(
    height=350,
    width=500,
    title="Score moyen par État",
    x_range=states
)

p1.vbar(
    x="state",
    top="score_moyen",
    width=0.7,
    color=factor_cmap("state", palette=Category20[20], factors=states),
    source=source_state_avg
)
p1.legend.visible = True
p1.legend.label_text_font_size = "11pt"
p1.legend.location = "top_right"
p1.xaxis.major_label_orientation = math.pi/3

p2 = figure(
    height=420,
    width=900,
    title="Évolution du score moyen par État",
    x_axis_label="Année",
    y_axis_label="Score moyen"
)

p2.multi_line(
    xs="years",
    ys="scores",
    color="colors",
    line_width=3,
    legend_field="labels",
    source=source_state_year
)

p2.legend.location = "top_left"
p2.legend.click_policy = "hide"
p2.legend.label_text_font_size = "12pt"

p3 = figure(
    height=350,
    width=500,
    title="Histogramme des scores par matière"
)

p3.quad(
    top="count",
    bottom=0,
    left="left",
    right="right",
    fill_color="color",
    alpha=0.6,
    line_color="black",
    source = source_hist
)

p3.legend.visible = True
p3.legend.label_text_font_size = "12pt"
p3.add_layout(p3.legend[0], 'right')

p4 = figure(
    height=420,
    width=900,
    x_range=matiere,
    title="Boxplot des scores par matière"
)
p4.add_layout(p4.legend[0], "right")
p4.legend.label_text_font_size = "12pt"


def compute_box_stats(df, col):
    q1 = df[col].quantile(0.25)
    q2 = df[col].quantile(0.50)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    upper = min(df[col].max(), q3 + 1.5*iqr)
    lower = max(df[col].min(), q1 - 1.5*iqr)
    return q1, q2, q3, upper, lower

for i, col in enumerate(matiere):
    q1, q2, q3, upper, lower = compute_box_stats(df, col)
    p4.segment([i], [lower], [i], [upper], line_width=2, legend_label=col)
    p4.vbar([i], 0.7, q2, q3, fill_color="#90CAF9", line_color="black")
    p4.vbar([i], 0.7, q1, q2, fill_color="#90CAF9", line_color="black")
    p4.rect([i], [q2], 0.7, 0.01, line_color="black")

def update_data():
    
    year = int(select_year.value)
    genders = [checkbox_gender.labels[i] for i in checkbox_gender.active]

    df_filtered = df[
        (df["year"] == year) &
        (df["gender"].isin(genders)) &
        (df["score_moyen"] >= slider_min_score.value)
    ]

    update_kpi(df_filtered)

    # --- Graph 1 ---
    df_state = df_filtered.groupby("state")["score_moyen"].mean().reset_index()
    source_state_avg.data = df_state

    # --- Graph 2 ---
    sel = select_states.value
    years_list = []
    scores_list = []
    colors = Spectral6[:len(sel)]

    for st in sel:
        tmp = df[df["state"] == st].sort_values("year")
        years_list.append(list(tmp["year"]))
        scores_list.append(list(tmp["score_moyen"]))

    source_state_year.data = {
    "years": years_list,
    "scores": scores_list,
    "colors": colors,
    "labels": sel
    }

    # --- Histogramme ---
    col = select_matiere.value
    counts, edges = np.histogram(df_filtered[col], bins=15)
    source_hist.data = {
        "left": edges[:-1],
        "right": edges[1:],
        "count": counts,
        "color": ["#4c72b0"]*len(counts)
    }

def _cb(attr, old, new):
    update_data()

# --- callbacks (en bas du fichier) ---
select_year.on_change("value", _cb)
select_states.on_change("value", _cb)
select_matiere.on_change("value", _cb)
slider_min_score.on_change("value", _cb)
checkbox_gender.on_change("active", _cb)


layout = column(
    Div(
        text="""
        <h1 style='
            text-align:center;
            font-size:42px;
            font-family:Segoe UI, Arial;
            color:#002855;
            margin-bottom:20px;
        '>
        Students Performance Dashboard
        </h1>
        """
    ),
    row(kpi1, kpi2, kpi3, kpi4),
    row(select_year, select_states, select_matiere, slider_min_score),
    row(checkbox_gender),
    row(p1, p3),
    p2,
    p4
)

curdoc().add_root(layout)
curdoc().title = "Students Performance Dashboard"
