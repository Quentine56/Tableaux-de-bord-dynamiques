"""
Students Performance Dashboard
------------------------------

Dashboard interactif permettant d'analyser les performances scolaires
des élèves américains. Génère des graphiques par État, par année,
ainsi que des analyses globales par matière.

Technologies utilisées :
- Streamlit
- Pandas
- Plotly Express
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image

st.set_page_config(
    page_title="Students Performance Dashboard",
    page_icon="",
    layout="wide"
)

st.title("Students Performance Dashboard (USA)")
st.markdown("Analyse interactive des performances scolaires des étudiants aux États-Unis.")

df = pd.read_csv("StudentsPerformance.csv")
df = df.drop(columns=["race/ethnicity"])

# Nettoyage des états (bug principal corrigé)
df["state"] = df["state"].astype(str).str.strip().str.title()

matiere = ["math score", "reading score", "writing score"]
df["score_moyen"] = df[matiere].mean(axis=1).round(2)

years = sorted(df["year"].unique())
states = sorted(df["state"].unique())

col1, col2, col3 = st.columns(3)

col1.metric("Score moyen général", f"{df['score_moyen'].mean():.2f}", delta="", help="Moyenne générale des trois matières.")
col2.metric("Score maximum", f"{df['score_moyen'].max():.2f}")
col3.metric("Score minimum", f"{df['score_moyen'].min():.2f}")

# Couleurs personnalisées
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #f0f4ff;
    padding: 12px;
    border-radius: 8px;
    margin: 5px;
}
div[data-testid="metric-container"]:nth-child(2) {
    background-color: #e9fbe9;
}
div[data-testid="metric-container"]:nth-child(3) {
    background-color: #ffecec;
}
</style>
""", unsafe_allow_html=True)

st.markdown("---")

st.header("Score moyen par État")

colA, colB = st.columns(2)

with colA:
    selected_year = st.selectbox("Sélectionner une année :", years)

with colB:
    selected_states = st.multiselect("Sélectionner des États :", states)

# Graphique score par État
year_df = df[df["year"] == selected_year]
state_avg = year_df.groupby("state")["score_moyen"].mean().reset_index()

fig1 = px.bar(
    state_avg,
    x="score_moyen",
    y="state",
    orientation="h",
    title=f"Score moyen par État - {selected_year}"
)

st.plotly_chart(fig1, use_container_width=True)

st.header("Évolution du score moyen par État")

if selected_states:
    # Filtrage robuste
    subset = df[df["state"].isin([s.title().strip() for s in selected_states])]

    state_year_avg = (
        subset.groupby(["state", "year"])["score_moyen"]
        .mean()
        .reset_index()
        .sort_values(["state", "year"])
    )

    fig2 = px.line(
        state_year_avg,
        x="year",
        y="score_moyen",
        color="state",
        markers=True,
        title="Évolution du score moyen par État"
    )

    fig2.update_layout(hovermode="x unified")

    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Sélectionner un ou plusieurs États pour afficher le graphique.")

st.header("Analyse globale")

fig_scatter = px.scatter(
    df,
    x="reading score",
    y="math score",
    color="gender",
    size="score_moyen",
    hover_name="state",
    title="Lecture vs Math"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# Histogrammes
fig_hist = px.histogram(
    df,
    x=matiere,
    barmode="overlay",
    title="Distribution des scores par matière"
)

st.plotly_chart(fig_hist, use_container_width=True)

st.header("Boxplot des scores par matière")

df_long = df.melt(
    value_vars=matiere,
    var_name="Matière",
    value_name="Score"
)

fig_box_matiere = px.box(
    df_long,
    x="Matière",
    y="Score",
    title="Distribution du score par matière"
)

st.plotly_chart(fig_box_matiere, use_container_width=True)

st.markdown("---")
