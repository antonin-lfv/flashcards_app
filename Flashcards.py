import streamlit as st
from config import CSS
from bdd_manager import (
    init_db,
    update_card_probability,
    update_stats,
    get_all_themes,
    get_number_of_cards,
)
import random
import sqlite3
import os

st.set_page_config(page_title="Flashcards", page_icon="📚", layout="wide")

st.markdown(CSS, unsafe_allow_html=True)

st.markdown("<p class='title'>Flashcards Application</p>", unsafe_allow_html=True)
st.divider()
st.write("#")

if not os.path.exists("flashcards.db"):
    init_db()

# Récupérer tous les thèmes
themes = get_all_themes()
theme_names = [theme[1] for theme in themes]  # theme[1] est le nom du thème

# Initialiser l'état de la session pour les thèmes sélectionnés
if "selected_themes" not in st.session_state:
    st.session_state["selected_themes"] = (
        theme_names.copy()
    )  # Tous les thèmes sélectionnés par défaut

st.sidebar.subheader(f"Nombre de carte total : {get_number_of_cards()}")

st.sidebar.write("#")

# Ajouter la sélection de thèmes dans la barre latérale
with st.sidebar.expander("Sélectionnez les thèmes"):
    if st.button("Ajouter tous les thèmes"):
        st.session_state["selected_themes"] = theme_names.copy()

    # Sélection multiple des thèmes avec liaison à st.session_state
    selected_themes = st.multiselect(
        "Thèmes à inclure dans la révision",
        options=theme_names,
        default=st.session_state["selected_themes"],
        key="selected_themes",
    )


def select_card_for_review(selected_themes, previous_card_id=None):
    if not selected_themes:
        return None  # Aucun thème sélectionné

    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    # Obtenir les id_theme correspondant aux thèmes sélectionnés
    selected_theme_ids = []
    for theme in themes:
        if theme[1] in selected_themes:
            selected_theme_ids.append(theme[0])  # theme[0] est l'id_theme

    placeholders = ",".join("?" * len(selected_theme_ids))
    base_query = f"SELECT id, question, reponse, theme, probabilite FROM cards WHERE id_theme IN ({placeholders})"
    params = selected_theme_ids.copy()

    # Obtenir toutes les cartes pour compter le nombre total
    c.execute(base_query, params)
    all_cards = c.fetchall()
    total_cards = len(all_cards)

    if total_cards == 0:
        conn.close()
        return None

    # Exclure la carte précédente si plus d'une carte est disponible
    if previous_card_id is not None and total_cards > 1:
        query = base_query + " AND id != ?"
        params.append(previous_card_id)
        c.execute(query, params)
        cards = c.fetchall()
        if not cards:
            # Si aucune carte n'est disponible après exclusion, inclure toutes les cartes
            c.execute(base_query, selected_theme_ids)
            cards = c.fetchall()
    else:
        cards = all_cards

    conn.close()

    if cards:
        # Créer une liste de probabilités normalisées
        probabilities = [card[4] for card in cards]  # card[4] est la probabilité
        total = sum(probabilities)
        normalized_probabilities = [p / total for p in probabilities]

        # Sélectionner une carte en fonction des probabilités normalisées
        selected_card = random.choices(cards, weights=normalized_probabilities, k=1)[0]
        return selected_card
    else:
        return None


# Initialiser l'état de la session pour stocker la carte actuelle
if "current_card" not in st.session_state:
    st.session_state["current_card"] = select_card_for_review(
        st.session_state["selected_themes"]
    )
    st.session_state["user_answer"] = ""
    st.session_state["show_result"] = False
    st.session_state["previous_card_id"] = (
        None  # Initialiser l'ID de la carte précédente
    )

# Si les thèmes sélectionnés changent, réinitialiser la carte actuelle
if "prev_selected_themes" not in st.session_state:
    st.session_state["prev_selected_themes"] = st.session_state[
        "selected_themes"
    ].copy()
else:
    if st.session_state["prev_selected_themes"] != st.session_state["selected_themes"]:
        st.session_state["current_card"] = select_card_for_review(
            st.session_state["selected_themes"]
        )
        st.session_state["user_answer"] = ""
        st.session_state["show_result"] = False
        st.session_state["prev_selected_themes"] = st.session_state[
            "selected_themes"
        ].copy()
        st.session_state["previous_card_id"] = (
            None  # Réinitialiser l'ID de la carte précédente
        )

card = st.session_state["current_card"]

_, main_col, _ = st.columns([1, 5, 1])

with main_col:
    with st.container(border=True):
        if card:
            st.markdown(f"### Thème : {card[3]}")
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"**Question :**")
            st.info(card[1])

            if not st.session_state["show_result"]:
                user_answer = st.text_area(
                    "Votre réponse", value=st.session_state["user_answer"]
                )
                if st.button("Valider"):
                    st.session_state["user_answer"] = user_answer
                    st.session_state["show_result"] = True
                    st.rerun()
            else:
                # Afficher la réponse de l'utilisateur et la bonne réponse côte à côte
                st.markdown("### Votre réponse vs La bonne réponse")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Votre réponse :**")
                    st.warning(st.session_state["user_answer"])
                with col2:
                    st.markdown("**La bonne réponse :**")
                    st.success(card[2])

                # Demander à l'utilisateur s'il a bien répondu
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("### Avez-vous correctement répondu ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Oui"):
                        is_correct = True
                        update_card_probability(card[0], is_correct)
                        update_stats(is_correct)
                        # Passer à la carte suivante
                        st.session_state["previous_card_id"] = card[
                            0
                        ]  # Enregistrer l'ID de la carte précédente
                        st.session_state["current_card"] = select_card_for_review(
                            st.session_state["selected_themes"],
                            st.session_state["previous_card_id"],
                        )
                        st.session_state["user_answer"] = ""
                        st.session_state["show_result"] = False
                        st.rerun()
                with col2:
                    if st.button("Non"):
                        is_correct = False
                        update_card_probability(card[0], is_correct)
                        update_stats(is_correct)
                        # Passer à la carte suivante
                        st.session_state["previous_card_id"] = card[
                            0
                        ]  # Enregistrer l'ID de la carte précédente
                        st.session_state["current_card"] = select_card_for_review(
                            st.session_state["selected_themes"],
                            st.session_state["previous_card_id"],
                        )
                        st.session_state["user_answer"] = ""
                        st.session_state["show_result"] = False
                        st.rerun()
        else:
            st.info("Aucune carte disponible pour le(s) thème(s) sélectionné(s).")
