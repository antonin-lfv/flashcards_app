import streamlit as st
from config import CSS
import pandas as pd
import plotly.express as px
from datetime import datetime
from bdd_manager import get_stats

st.set_page_config(page_title="Statistiques", page_icon="📚", layout="wide")

st.markdown(CSS, unsafe_allow_html=True)

st.markdown("<p class='title'>Vos statistiques</p>", unsafe_allow_html=True)
st.divider()

# Récupérer les statistiques
stats = get_stats()

if stats:
    # Créer un DataFrame à partir des données
    columns = ["id", "bonnes_reponses", "mauvaises_reponses", "date"]
    df_stats = pd.DataFrame(stats, columns=columns)

    # Convertir la colonne 'date' en type datetime
    df_stats["date"] = pd.to_datetime(df_stats["date"])

    # Trier par date
    df_stats = df_stats.sort_values("date")

    # Préparer les données pour le graphique linéaire
    df_melted = df_stats.melt(
        id_vars="date",
        value_vars=["bonnes_reponses", "mauvaises_reponses"],
        var_name="Type de réponse",
        value_name="Nombre",
    )

    # Créer le graphique linéaire
    fig_line = px.line(
        df_melted,
        x="date",
        y="Nombre",
        color="Type de réponse",
        markers=True,
        title="Évolution des réponses correctes et incorrectes par jour",
        color_discrete_map={
            "bonnes_reponses": "#2ca02c",
            "mauvaises_reponses": "#d62728",
        },
    )

    # Uniquement la date, sans l'heure
    fig_line.update_xaxes(tickformat="%d/%m/%Y")

    # Afficher le graphique linéaire
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # Obtenir les données pour aujourd'hui
    today = datetime.now().strftime("%Y-%m-%d")
    df_today = df_stats[df_stats["date"] == today]

    if not df_today.empty:
        bonnes_reponses_today = df_today["bonnes_reponses"].values[0]
        mauvaises_reponses_today = df_today["mauvaises_reponses"].values[0]

        data = {
            "Type de réponse": ["Bonnes réponses", "Mauvaises réponses"],
            "Nombre": [bonnes_reponses_today, mauvaises_reponses_today],
        }

        df_pie = pd.DataFrame(data)

        # Créer le diagramme en anneau (vert pour les bonnes réponses, rouge pour les mauvaises réponses)
        fig_donut = px.pie(
            df_pie,
            values="Nombre",
            names="Type de réponse",
            hole=0.4,
            title="Répartition des réponses d'aujourd'hui",
            color=["Bonnes réponses", "Mauvaises réponses"],
            color_discrete_map={
                "Bonnes réponses": "#2ca02c",
                "Mauvaises réponses": "#d62728",
            },
        )

        fig_donut.update_traces(textinfo="percent+label", textposition="outside")

        # Afficher le diagramme en anneau
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Aucune donnée pour aujourd'hui.")
else:
    st.info("Aucune donnée statistique disponible.")
