import streamlit as st
from config import CSS
from bdd_manager import (
    create_theme,
    get_all_themes,
    create_card,
    get_cards_by_theme,
    update_card,
    delete_card,
    delete_theme,
)


st.set_page_config(page_title="Configuration", page_icon="📚", layout="wide")

st.markdown(CSS, unsafe_allow_html=True)

st.markdown("<p class='title'>Configuration</p>", unsafe_allow_html=True)

st.write("##")

st.subheader("Gérer les thèmes")

c1_theme, _, c2_theme = st.columns((1, 0.5, 1))

with c1_theme:
    # Formulaire pour ajouter un nouveau thème
    with st.form("add_theme_form"):
        theme_name = st.text_input("Nom du thème à ajouter")
        submit_theme = st.form_submit_button("Ajouter le thème")
        if submit_theme:
            if theme_name:
                # Récupérer tous les thèmes existants
                themes = get_all_themes()
                theme_names = [theme[1].lower() for theme in themes]
                if theme_name.lower() in theme_names:
                    st.error(f"Le thème '{theme_name}' existe déjà.")
                else:
                    create_theme(theme_name)
                    st.rerun()
                    st.success(f"Thème '{theme_name}' ajouté avec succès.")
            else:
                st.error("Veuillez entrer un nom de thème.")

with c2_theme:
    # Formulaire pour supprimer un thème
    with st.form("delete_theme_form"):
        # Récupérer tous les thèmes
        themes = get_all_themes()
        if themes:
            theme_names = [theme[1] for theme in themes]
            selected_theme_to_delete = st.selectbox(
                "Sélectionnez un thème à supprimer", theme_names
            )
            submit_delete_theme = st.form_submit_button("Supprimer le thème")
            if submit_delete_theme:
                if selected_theme_to_delete:
                    # Obtenir l'id_theme pour le thème sélectionné
                    id_theme_to_delete = None
                    for theme in themes:
                        if theme[1] == selected_theme_to_delete:
                            id_theme_to_delete = theme[0]
                            break
                    if id_theme_to_delete is not None:
                        # Vérifier s'il y a des flashcards associées à ce thème
                        cards_in_theme = get_cards_by_theme(id_theme_to_delete)
                        if cards_in_theme:
                            st.error(
                                "Impossible de supprimer le thème car des flashcards y sont associées."
                            )
                        else:
                            delete_theme(id_theme_to_delete)
                            st.rerun()
                            st.success(
                                f"Thème '{selected_theme_to_delete}' supprimé avec succès."
                            )
                    else:
                        st.error("Erreur lors de la récupération de l'ID du thème.")
                else:
                    st.error("Veuillez sélectionner un thème à supprimer.")
        else:
            st.info("Aucun thème disponible à supprimer.")

st.write("##")


# Formulaire pour ajouter une nouvelle flashcard
st.subheader("Ajouter une nouvelle flashcard")
# Récupérer tous les thèmes pour le sélecteur
themes = get_all_themes()
theme_names = [theme[1] for theme in themes]  # theme[1] est le nom du thème

with st.form("add_flashcard_form"):
    question = st.text_input("Question")
    answer = st.text_input("Réponse")
    selected_theme = st.selectbox("Thème", theme_names)

    submit_flashcard = st.form_submit_button("Ajouter la flashcard")
    if submit_flashcard:
        if question and answer and selected_theme:
            # Obtenir l'id_theme pour le thème sélectionné
            id_theme = None
            for theme in themes:
                if theme[1] == selected_theme:
                    id_theme = theme[0]  # theme[0] est l'id_theme
                    break
            if id_theme is not None:
                create_card(question, answer, selected_theme, 0.5, id_theme)
                st.success(
                    f"Flashcard ajoutée avec succès au thème '{selected_theme}'."
                )
            else:
                st.error("Erreur lors de la récupération de l'ID du thème.")
        else:
            st.error("Veuillez remplir tous les champs du formulaire.")

st.write("##")


# Section pour afficher les flashcards par thème
st.subheader("Afficher les flashcards par thème")

# Sélecteur de thème pour afficher les flashcards
selected_theme_display = st.selectbox(
    "Sélectionnez un thème pour afficher les flashcards", theme_names
)

st.write("")

if selected_theme_display:
    # Obtenir l'id_theme pour le thème sélectionné
    id_theme = None
    for theme in themes:
        if theme[1] == selected_theme_display:
            id_theme = theme[0]  # theme[0] est l'id_theme
            break

    if id_theme is not None:
        # Récupérer toutes les flashcards pour ce thème
        cards = get_cards_by_theme(id_theme)

        if cards:
            for card in cards:
                with st.container(border=True):
                    st.write(f"**Question**: {card[1]}")  # card[1] est la question
                    st.write(f"**Réponse**: {card[2]}")  # card[2] est la réponse

                    # Créer des clés uniques pour les widgets et l'état
                    update_button_key = f"update_button_{card[0]}"
                    delete_button_key = f"delete_button_{card[0]}"
                    update_form_key = f"show_update_form_{card[0]}"
                    delete_confirm_key = f"show_delete_confirm_{card[0]}"

                    # Initialiser les variables de session pour chaque flashcard
                    if update_form_key not in st.session_state:
                        st.session_state[update_form_key] = False
                    if delete_confirm_key not in st.session_state:
                        st.session_state[delete_confirm_key] = False

                    # Définir les fonctions de rappel pour les boutons
                    def toggle_update_form(card_id):
                        key = f"show_update_form_{card_id}"
                        st.session_state[key] = not st.session_state[key]

                    def toggle_delete_confirm(card_id):
                        key = f"show_delete_confirm_{card_id}"
                        st.session_state[key] = not st.session_state[key]

                    col1, col2, _ = st.columns((1, 1, 5))
                    with col1:
                        st.button(
                            "Mettre à jour",
                            key=update_button_key,
                            on_click=toggle_update_form,
                            args=(card[0],),
                        )
                    with col2:
                        st.button(
                            "Supprimer",
                            key=delete_button_key,
                            on_click=toggle_delete_confirm,
                            args=(card[0],),
                        )

                    # Afficher le formulaire de mise à jour si le bouton a été cliqué
                    if st.session_state[update_form_key]:
                        with st.form(f"update_form_{card[0]}"):
                            new_question = st.text_input("Question", value=card[1])
                            new_answer = st.text_input("Réponse", value=card[2])
                            new_theme = st.selectbox(
                                "Thème",
                                theme_names,
                                index=theme_names.index(selected_theme_display),
                                key=f"update_theme_{card[0]}",
                            )
                            submit_update = st.form_submit_button("Mettre à jour")
                            if submit_update:
                                # Obtenir l'id_theme pour le nouveau thème
                                new_id_theme = None
                                for theme in themes:
                                    if theme[1] == new_theme:
                                        new_id_theme = theme[0]
                                        break
                                if new_id_theme is not None:
                                    print(card)
                                    update_card(
                                        card[0],
                                        new_question,
                                        new_answer,
                                        new_theme,
                                        card[4],
                                        new_id_theme,
                                    )
                                    st.success("Flashcard mise à jour avec succès.")
                                    st.session_state[update_form_key] = (
                                        False  # Fermer le formulaire
                                    )
                                    st.rerun()
                                else:
                                    st.error("Erreur lors de la mise à jour du thème.")

                    # Afficher la confirmation de suppression si le bouton a été cliqué
                    if st.session_state[delete_confirm_key]:
                        st.warning("Voulez-vous vraiment supprimer cette flashcard ?")
                        if st.button(
                            "Confirmer la suppression", key=f"confirm_delete_{card[0]}"
                        ):
                            delete_card(card[0])
                            st.success("Flashcard supprimée avec succès.")
                            st.session_state[delete_confirm_key] = (
                                False  # Fermer la confirmation
                            )
                            st.rerun()
        else:
            st.info("Aucune flashcard trouvée pour ce thème.")
    else:
        st.error("Erreur lors de la récupération de l'ID du thème.")
